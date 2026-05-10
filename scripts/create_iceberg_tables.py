#!/usr/bin/env python3
"""
Script para crear tablas Iceberg en las capas Bronze, Silver y Gold
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, MapType
import sys

def create_spark_session():
    """Crear sesión de Spark con configuración de Iceberg"""
    spark = SparkSession.builder \
        .appName("create_iceberg_tables") \
        .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.iceberg.type", "hive") \
        .config("spark.sql.catalog.iceberg.uri", "thrift://hive-metastore:9083") \
        .config("spark.sql.catalog.iceberg.warehouse", "s3a://iceberg-data") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "changeme123!") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.defaultCatalog", "iceberg") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("INFO")
    return spark

def create_namespaces(spark):
    """Crear namespaces para las capas medallion"""
    print("Creando namespaces...")
    try:
        spark.sql("CREATE NAMESPACE IF NOT EXISTS bronze COMMENT 'Raw data layer'")
        spark.sql("CREATE NAMESPACE IF NOT EXISTS silver COMMENT 'Curated data layer'")
        spark.sql("CREATE NAMESPACE IF NOT EXISTS gold COMMENT 'Serving/analytics data layer'")
        print("✅ Namespaces creados exitosamente")
    except Exception as e:
        print(f"⚠️  Error al crear namespaces: {e}")
        return False
    return True

def create_bronze_tables(spark):
    """Crear tablas en capa Bronze"""
    print("\nCreando tablas Bronze...")
    
    try:
        # Tabla de eventos raw
        spark.sql("""
            CREATE TABLE IF NOT EXISTS bronze.raw_events (
                event_id STRING,
                event_time TIMESTAMP,
                source_system STRING,
                user_id STRING,
                raw_payload STRING,
                ingestion_time TIMESTAMP,
                file_name STRING
            )
            USING ICEBERG
            PARTITIONED BY (year(event_time), month(event_time), day(event_time))
            LOCATION 's3a://iceberg-data/bronze/raw_events/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy',
                'write.metadata.compression-codec'='gzip'
            )
        """)
        print("✅ Tabla bronze.raw_events creada")
        
        # Tabla de logs
        spark.sql("""
            CREATE TABLE IF NOT EXISTS bronze.raw_logs (
                log_id STRING,
                log_time TIMESTAMP,
                level STRING,
                message STRING,
                source_system STRING,
                raw_content STRING,
                ingestion_time TIMESTAMP
            )
            USING ICEBERG
            PARTITIONED BY (year(log_time), month(log_time), day(log_time))
            LOCATION 's3a://iceberg-data/bronze/raw_logs/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy'
            )
        """)
        print("✅ Tabla bronze.raw_logs creada")
        
    except Exception as e:
        print(f"❌ Error al crear tablas Bronze: {e}")
        return False
    
    return True

def create_silver_tables(spark):
    """Crear tablas en capa Silver"""
    print("\nCreando tablas Silver...")
    
    try:
        # Tabla de eventos curados
        spark.sql("""
            CREATE TABLE IF NOT EXISTS silver.events (
                event_id STRING,
                event_time TIMESTAMP,
                user_id STRING,
                event_type STRING,
                event_category STRING,
                properties MAP<STRING, STRING>,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            USING ICEBERG
            PARTITIONED BY (year(event_time), month(event_time))
            LOCATION 's3a://iceberg-data/silver/events/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy'
            )
        """)
        print("✅ Tabla silver.events creada")
        
        # Tabla de usuarios
        spark.sql("""
            CREATE TABLE IF NOT EXISTS silver.users (
                user_id STRING,
                user_name STRING,
                email STRING,
                country STRING,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            USING ICEBERG
            LOCATION 's3a://iceberg-data/silver/users/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy'
            )
        """)
        print("✅ Tabla silver.users creada")
        
    except Exception as e:
        print(f"❌ Error al crear tablas Silver: {e}")
        return False
    
    return True

def create_gold_tables(spark):
    """Crear tablas en capa Gold"""
    print("\nCreando tablas Gold...")
    
    try:
        # Tabla de métricas diarias por usuario
        spark.sql("""
            CREATE TABLE IF NOT EXISTS gold.daily_user_metrics (
                date DATE,
                user_id STRING,
                total_events INT,
                unique_event_types INT,
                first_event_time TIMESTAMP,
                last_event_time TIMESTAMP,
                created_at TIMESTAMP
            )
            USING ICEBERG
            PARTITIONED BY (year(date), month(date))
            LOCATION 's3a://iceberg-data/gold/daily_user_metrics/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy'
            )
        """)
        print("✅ Tabla gold.daily_user_metrics creada")
        
        # Tabla de eventos por tipo
        spark.sql("""
            CREATE TABLE IF NOT EXISTS gold.event_types_daily (
                date DATE,
                event_type STRING,
                event_count INT,
                unique_users INT,
                created_at TIMESTAMP
            )
            USING ICEBERG
            PARTITIONED BY (year(date), month(date))
            LOCATION 's3a://iceberg-data/gold/event_types_daily/'
            TBLPROPERTIES (
                'write.format.default'='parquet',
                'write.parquet.compression-codec'='snappy'
            )
        """)
        print("✅ Tabla gold.event_types_daily creada")
        
    except Exception as e:
        print(f"❌ Error al crear tablas Gold: {e}")
        return False
    
    return True

def verify_tables(spark):
    """Verificar que todas las tablas fueron creadas"""
    print("\nVerificando tablas creadas...")
    
    try:
        tables = spark.sql("SELECT * FROM (SHOW TABLES IN bronze) UNION ALL (SHOW TABLES IN silver) UNION ALL (SHOW TABLES IN gold)").collect()
        print(f"✅ Total de tablas creadas: {len(tables)}")
        
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"⚠️  Error al verificar tablas: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("Creación de tablas Iceberg - OpenData")
    print("=" * 60)
    
    try:
        spark = create_spark_session()
        
        # Crear namespaces
        if not create_namespaces(spark):
            sys.exit(1)
        
        # Crear tablas de cada capa
        if not create_bronze_tables(spark):
            sys.exit(1)
        
        if not create_silver_tables(spark):
            sys.exit(1)
        
        if not create_gold_tables(spark):
            sys.exit(1)
        
        # Verificar creación
        verify_tables(spark)
        
        print("\n" + "=" * 60)
        print("✅ Creación de tablas completada exitosamente")
        print("=" * 60)
        
        spark.stop()
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
