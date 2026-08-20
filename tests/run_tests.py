#!/usr/bin/env python3
"""
Ejecutor de tests para OpenData.
Usa unittest (stdlib) — no requiere pip install.

Uso:
    python3 tests/run_tests.py
    python3 tests/run_tests.py -v
"""

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")

sys.path.insert(0, SCRIPTS_DIR)

try:
    import pyspark  # noqa: F401
    HAS_PYSPARK = True
except ImportError:
    HAS_PYSPARK = False

requires_pyspark = unittest.skipUnless(HAS_PYSPARK, "pyspark not installed")


class TestGetSparkConfig(unittest.TestCase):
    def test_returns_dict(self):
        from config import get_spark_config
        config = get_spark_config()
        self.assertIsInstance(config, dict)

    def test_contains_all_required_keys(self):
        from config import get_spark_config
        required = [
            "spark.sql.catalog.iceberg",
            "spark.sql.catalog.iceberg.type",
            "spark.sql.catalog.iceberg.uri",
            "spark.sql.catalog.iceberg.warehouse",
            "spark.hadoop.fs.s3a.endpoint",
            "spark.hadoop.fs.s3a.access.key",
            "spark.hadoop.fs.s3a.secret.key",
            "spark.hadoop.fs.s3a.path.style.access",
            "spark.hadoop.fs.s3a.connection.ssl.enabled",
            "spark.sql.extensions",
            "spark.sql.defaultCatalog",
        ]
        config = get_spark_config()
        for key in required:
            self.assertIn(key, config, f"Missing key: {key}")

    def test_catalog_type_is_hive(self):
        from config import get_spark_config
        self.assertEqual(get_spark_config()["spark.sql.catalog.iceberg.type"], "hive")

    def test_default_catalog_is_iceberg(self):
        from config import get_spark_config
        self.assertEqual(get_spark_config()["spark.sql.defaultCatalog"], "iceberg")

    def test_env_var_overrides_access_key(self):
        from config import get_spark_config
        os.environ["AWS_ACCESS_KEY_ID"] = "my-custom-key"
        try:
            self.assertEqual(get_spark_config()["spark.hadoop.fs.s3a.access.key"], "my-custom-key")
        finally:
            del os.environ["AWS_ACCESS_KEY_ID"]

    def test_env_var_overrides_secret_key(self):
        from config import get_spark_config
        os.environ["AWS_SECRET_ACCESS_KEY"] = "my-secret"
        try:
            self.assertEqual(get_spark_config()["spark.hadoop.fs.s3a.secret.key"], "my-secret")
        finally:
            del os.environ["AWS_SECRET_ACCESS_KEY"]

    def test_defaults_when_no_env_vars(self):
        from config import get_spark_config
        for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_ENDPOINT",
                     "ICEBERG_METASTORE_URI", "ICEBERG_WAREHOUSE"]:
            os.environ.pop(key, None)
        config = get_spark_config()
        self.assertEqual(config["spark.hadoop.fs.s3a.access.key"], "minioadmin")
        self.assertEqual(config["spark.hadoop.fs.s3a.secret.key"], "changeme123!")
        self.assertEqual(config["spark.hadoop.fs.s3a.endpoint"], "http://minio:9000")


class TestScriptsImportable(unittest.TestCase):
    def test_config_module_imports(self):
        import config
        self.assertTrue(hasattr(config, "create_spark_session"))
        self.assertTrue(hasattr(config, "get_spark_config"))

    def test_ingest_module_has_generate_function(self):
        from ingest_bronze_data import generate_sample_events
        self.assertTrue(callable(generate_sample_events))

    @requires_pyspark
    def test_create_tables_module_has_functions(self):
        from create_iceberg_tables import create_namespaces, create_bronze_tables
        self.assertTrue(callable(create_namespaces))
        self.assertTrue(callable(create_bronze_tables))

    @requires_pyspark
    def test_transform_module_has_function(self):
        from transform_silver_data import transform_bronze_to_silver
        self.assertTrue(callable(transform_bronze_to_silver))

    @requires_pyspark
    def test_aggregate_module_has_functions(self):
        from aggregate_gold_data import aggregate_daily_metrics, aggregate_event_types_daily
        self.assertTrue(callable(aggregate_daily_metrics))
        self.assertTrue(callable(aggregate_event_types_daily))


class TestGenerateSampleEvents(unittest.TestCase):
    def test_returns_correct_count(self):
        from ingest_bronze_data import generate_sample_events
        events = generate_sample_events(100)
        self.assertEqual(len(events), 100)

    def test_returns_correct_count_zero(self):
        from ingest_bronze_data import generate_sample_events
        events = generate_sample_events(0)
        self.assertEqual(len(events), 0)

    def test_default_count_is_1000(self):
        from ingest_bronze_data import generate_sample_events
        events = generate_sample_events()
        self.assertEqual(len(events), 1000)

    def test_all_required_fields_present(self):
        from ingest_bronze_data import generate_sample_events
        required = ["event_id", "event_time", "source_system", "user_id",
                     "raw_payload", "ingestion_time", "file_name"]
        events = generate_sample_events(10)
        for event in events:
            for field in required:
                self.assertIn(field, event, f"Missing field '{field}'")

    def test_event_ids_are_unique(self):
        from ingest_bronze_data import generate_sample_events
        events = generate_sample_events(200)
        ids = [e["event_id"] for e in events]
        self.assertEqual(len(ids), len(set(ids)))

    def test_source_systems_valid(self):
        from ingest_bronze_data import generate_sample_events
        valid = {"mobile", "web", "api", "backend"}
        events = generate_sample_events(100)
        for event in events:
            self.assertIn(event["source_system"], valid)

    def test_raw_payload_is_valid_json(self):
        import json
        from ingest_bronze_data import generate_sample_events
        events = generate_sample_events(20)
        for event in events:
            payload = json.loads(event["raw_payload"])
            self.assertIsInstance(payload, dict)
            self.assertIn("action", payload)
            self.assertIn("session_id", payload)
            self.assertIn("duration", payload)


class TestTransformLogic(unittest.TestCase):
    def _make_event(self, **overrides):
        base = {
            "event_id": "e1", "event_time": "2026-01-01",
            "source_system": "web", "user_id": "u1",
            "raw_payload": '{"action":"click"}',
            "ingestion_time": "2026-01-01", "file_name": "f.json",
        }
        base.update(overrides)
        return base

    def test_null_filter_removes_events_without_id(self):
        events = [self._make_event(event_id="e1"), self._make_event(event_id=None)]
        filtered = [e for e in events if e["event_id"] is not None]
        self.assertEqual(len(filtered), 1)

    def test_null_filter_removes_events_without_user(self):
        events = [self._make_event(user_id="u1"), self._make_event(user_id=None)]
        filtered = [e for e in events if e["user_id"] is not None]
        self.assertEqual(len(filtered), 1)

    def test_silver_schema_fields(self):
        silver_fields = ["event_id", "event_time", "user_id", "event_type",
                         "event_category", "properties", "created_at", "updated_at"]
        self.assertEqual(len(silver_fields), 8)
        self.assertIn("event_type", silver_fields)
        self.assertIn("properties", silver_fields)

    def test_bronze_to_silver_field_mapping(self):
        bronze = self._make_event()
        silver = {
            "event_id": bronze["event_id"],
            "event_time": bronze["event_time"],
            "user_id": bronze["user_id"],
            "event_type": bronze["source_system"],
            "event_category": "default",
            "properties": {},
            "created_at": bronze["ingestion_time"],
            "updated_at": "now",
        }
        self.assertEqual(silver["event_id"], bronze["event_id"])
        self.assertEqual(silver["created_at"], bronze["ingestion_time"])


class TestDockerCompose(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import yaml
        compose_path = os.path.join(ROOT_DIR, "docker", "docker-compose.yml")
        if not os.path.exists(compose_path):
            raise unittest.SkipTest("docker-compose.yml not found")
        with open(compose_path) as f:
            cls.compose = yaml.safe_load(f)

    def test_compose_is_valid_yaml(self):
        self.assertIsNotNone(self.compose)
        self.assertIn("services", self.compose)

    def test_has_required_services(self):
        required = ["postgres", "minio", "hive-metastore", "spark-master",
                     "spark-worker-1", "spark-worker-2", "trino", "superset"]
        services = self.compose["services"]
        for name in required:
            self.assertIn(name, services, f"Missing service: {name}")

    def test_spark_master_port(self):
        master = self.compose["services"]["spark-master"]
        ports = [str(p) for p in master.get("ports", [])]
        self.assertTrue(any("8080" in p for p in ports))

    def test_minio_ports(self):
        minio = self.compose["services"]["minio"]
        ports = [str(p) for p in minio.get("ports", [])]
        self.assertTrue(any("9000" in p for p in ports))

    def test_superset_port(self):
        superset = self.compose["services"]["superset"]
        ports = [str(p) for p in superset.get("ports", [])]
        self.assertTrue(any("8088" in p for p in ports))


class TestEnvFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_path = os.path.join(ROOT_DIR, "docker", ".env")
        if not os.path.exists(env_path):
            raise unittest.SkipTest(".env not found")
        cls.env = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    cls.env[key.strip()] = value.strip()

    def test_required_vars_present(self):
        required = ["POSTGRES_USER", "POSTGRES_PASSWORD", "MINIO_ROOT_USER",
                     "MINIO_ROOT_PASSWORD", "AWS_ACCESS_KEY_ID",
                     "AWS_SECRET_ACCESS_KEY", "AWS_S3_ENDPOINT",
                     "ICEBERG_WAREHOUSE"]
        for var in required:
            self.assertIn(var, self.env, f"Missing env var: {var}")

    def test_s3_endpoint_format(self):
        self.assertTrue(self.env["AWS_S3_ENDPOINT"].startswith("http://"))

    def test_warehouse_format(self):
        self.assertTrue(self.env["ICEBERG_WAREHOUSE"].startswith("s3a://"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
