import os

import pytest
import yaml


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCKER_DIR = os.path.join(ROOT_DIR, "docker")
COMPOSE_FILE = os.path.join(DOCKER_DIR, "docker-compose.yml")
ENV_FILE = os.path.join(DOCKER_DIR, ".env")

REQUIRED_SERVICES = [
    "postgres",
    "minio",
    "hive-metastore",
    "spark-master",
    "spark-worker-1",
    "spark-worker-2",
    "trino",
    "superset",
    "airflow-webserver",
    "airflow-scheduler",
]

REQUIRED_ENV_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "MINIO_ROOT_USER",
    "MINIO_ROOT_PASSWORD",
    "SUPERSET_SECRET_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_S3_ENDPOINT",
    "ICEBERG_WAREHOUSE",
    "ICEBERG_METASTORE_URI",
]


class TestDockerCompose:
    @pytest.fixture(autouse=True)
    def load_compose(self):
        if not os.path.exists(COMPOSE_FILE):
            pytest.skip("docker-compose.yml not found")
        with open(COMPOSE_FILE) as f:
            self.compose = yaml.safe_load(f)

    def test_compose_file_is_valid_yaml(self):
        assert self.compose is not None
        assert "services" in self.compose

    def test_has_all_required_services(self):
        services = self.compose["services"]
        for name in REQUIRED_SERVICES:
            assert name in services, f"Missing service: {name}"

    def test_spark_master_has_port_mapping(self):
        services = self.compose["services"]
        master = services["spark-master"]
        assert "ports" in master
        port_strings = [str(p) for p in master["ports"]]
        assert any("8080" in p for p in port_strings)

    def test_minio_has_port_mapping(self):
        services = self.compose["services"]
        minio = services["minio"]
        assert "ports" in minio
        port_strings = [str(p) for p in minio["ports"]]
        assert any("9000" in p for p in port_strings)
        assert any("9001" in p for p in port_strings)

    def test_superset_has_port_mapping(self):
        services = self.compose["services"]
        superset = services["superset"]
        assert "ports" in superset
        port_strings = [str(p) for p in superset["ports"]]
        assert any("8088" in p for p in port_strings)

    def test_uses_opendata_network(self):
        services = self.compose["services"]
        for name, svc in services.items():
            if "networks" in svc:
                nets = svc["networks"]
                if isinstance(nets, list):
                    assert "opendata-network" in nets, f"{name} missing opendata-network"
                elif isinstance(nets, dict):
                    assert "opendata-network" in nets, f"{name} missing opendata-network"


class TestEnvFile:
    @pytest.fixture(autouse=True)
    def load_env(self):
        if not os.path.exists(ENV_FILE):
            pytest.skip(".env not found")
        self.env = {}
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    self.env[key.strip()] = value.strip()

    def test_has_all_required_vars(self):
        for var in REQUIRED_ENV_VARS:
            assert var in self.env, f"Missing env var: {var}"

    def test_postgres_user_is_set(self):
        assert len(self.env.get("POSTGRES_USER", "")) > 0

    def test_minio_root_user_is_set(self):
        assert len(self.env.get("MINIO_ROOT_USER", "")) > 0

    def test_s3_endpoint_format(self):
        endpoint = self.env.get("AWS_S3_ENDPOINT", "")
        assert endpoint.startswith("http://") or endpoint.startswith("https://")

    def test_warehouse_format(self):
        warehouse = self.env.get("ICEBERG_WAREHOUSE", "")
        assert warehouse.startswith("s3a://")
