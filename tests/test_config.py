import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from config import get_spark_config


REQUIRED_CONFIG_KEYS = [
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


class TestGetSparkConfig:
    def test_returns_dict(self):
        config = get_spark_config()
        assert isinstance(config, dict)

    def test_contains_all_required_keys(self):
        config = get_spark_config()
        for key in REQUIRED_CONFIG_KEYS:
            assert key in config, f"Missing key: {key}"

    def test_catalog_type_is_hive(self):
        config = get_spark_config()
        assert config["spark.sql.catalog.iceberg.type"] == "hive"

    def test_default_catalog_is_iceberg(self):
        config = get_spark_config()
        assert config["spark.sql.defaultCatalog"] == "iceberg"

    def test_path_style_access_enabled(self):
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.path.style.access"] == "true"

    def test_ssl_disabled_by_default(self):
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.connection.ssl.enabled"] == "false"

    def test_env_var_overrides_access_key(self, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "my-custom-key")
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.access.key"] == "my-custom-key"

    def test_env_var_overrides_secret_key(self, monkeypatch):
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "my-secret")
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.secret.key"] == "my-secret"

    def test_env_var_overrides_endpoint(self, monkeypatch):
        monkeypatch.setenv("AWS_S3_ENDPOINT", "http://custom-minio:9000")
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.endpoint"] == "http://custom-minio:9000"

    def test_env_var_overrides_metastore_uri(self, monkeypatch):
        monkeypatch.setenv("ICEBERG_METASTORE_URI", "thrift://custom:9083")
        config = get_spark_config()
        assert config["spark.sql.catalog.iceberg.uri"] == "thrift://custom:9083"

    def test_env_var_overrides_warehouse(self, monkeypatch):
        monkeypatch.setenv("ICEBERG_WAREHOUSE", "s3a://my-bucket")
        config = get_spark_config()
        assert config["spark.sql.catalog.iceberg.warehouse"] == "s3a://my-bucket"

    def test_defaults_when_no_env_vars(self, monkeypatch):
        for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_ENDPOINT",
                     "ICEBERG_METASTORE_URI", "ICEBERG_WAREHOUSE"]:
            monkeypatch.delenv(key, raising=False)
        config = get_spark_config()
        assert config["spark.hadoop.fs.s3a.access.key"] == "minioadmin"
        assert config["spark.hadoop.fs.s3a.secret.key"] == "changeme123!"
        assert config["spark.hadoop.fs.s3a.endpoint"] == "http://minio:9000"
        assert config["spark.sql.catalog.iceberg.uri"] == "thrift://hive-metastore:9083"
        assert config["spark.sql.catalog.iceberg.warehouse"] == "s3a://iceberg-data"


class TestScriptsImportable:
    def test_config_module_imports(self):
        import config
        assert hasattr(config, "create_spark_session")
        assert hasattr(config, "get_spark_config")

    def test_ingest_module_has_generate_function(self):
        from ingest_bronze_data import generate_sample_events
        assert callable(generate_sample_events)

    def test_create_tables_module_has_functions(self):
        from create_iceberg_tables import create_namespaces, create_bronze_tables
        assert callable(create_namespaces)
        assert callable(create_bronze_tables)

    def test_transform_module_has_function(self):
        from transform_silver_data import transform_bronze_to_silver
        assert callable(transform_bronze_to_silver)

    def test_aggregate_module_has_functions(self):
        from aggregate_gold_data import aggregate_daily_metrics, aggregate_event_types_daily
        assert callable(aggregate_daily_metrics)
        assert callable(aggregate_event_types_daily)
