#!/usr/bin/env python3
"""
Módulo de configuración compartido para los scripts ETL.
Lee credenciales y configuración desde variables de entorno,
con fallback a valores por defecto para desarrollo local.
"""

import os


def get_spark_config():
    """Retorna dict con la configuración de Spark para Iceberg/MinIO.

    Lee de variables de entorno cuando están disponibles,
    usa valores por defecto iguales a docker/.env para local dev.
    """
    return {
        "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
        "spark.sql.catalog.iceberg.type": "hive",
        "spark.sql.catalog.iceberg.uri": os.environ.get(
            "ICEBERG_METASTORE_URI", "thrift://hive-metastore:9083"
        ),
        "spark.sql.catalog.iceberg.warehouse": os.environ.get(
            "ICEBERG_WAREHOUSE", "s3a://iceberg-data"
        ),
        "spark.hadoop.fs.s3a.endpoint": os.environ.get(
            "AWS_S3_ENDPOINT", "http://minio:9000"
        ),
        "spark.hadoop.fs.s3a.access.key": os.environ.get(
            "AWS_ACCESS_KEY_ID", "minioadmin"
        ),
        "spark.hadoop.fs.s3a.secret.key": os.environ.get(
            "AWS_SECRET_ACCESS_KEY", "changeme123!"
        ),
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        "spark.sql.defaultCatalog": "iceberg",
    }


def create_spark_session(app_name="opendata_etl"):
    """Crear sesión de Spark con configuración de Iceberg/MinIO.

    Args:
        app_name: Nombre de la aplicación Spark.

    Returns:
        SparkSession configurada y lista para usar.
    """
    from pyspark.sql import SparkSession

    builder = SparkSession.builder.appName(app_name)

    for key, value in get_spark_config().items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("INFO")
    return spark
