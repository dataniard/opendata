#!/usr/bin/env python3
"""
Script de transformación: Bronze → Silver
Limpia y enriquece los datos crudos para la capa Silver
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json, lit, current_timestamp, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, MapType
import json
import sys

def create_spark_session():
    """Crear sesión de Spark con configuración de Iceberg"""
    spark = SparkSession.builder \
        .appName("transform_bronze_to_silver") \
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

def transform_bronze_to_silver(spark):
    """Transformar datos de Bronze a Silver"""
    print("\n" + "=" * 60)
    print("Transformación: Bronze → Silver")
    print("=" * 60)
    
    try:
        # Leer datos de Bronze
        print("\n1. Leyendo datos de bronze.raw_events...")
        bronze_df = spark.table("bronze.raw_events")
        print(f"   ✅ {bronze_df.count()} registros leídos")
        
        # Transformaciones
        print("\n2. Aplicando transformaciones...")
        
        # Parsear el payload JSON
        payload_schema = schema_of_json(lit('{"action": "click", "session_id": "session_1000", "duration": 100}'))
        
        # Transformar y enriquecer
        silver_df = bronze_df \
            .filter(col("event_id").isNotNull()) \
            .filter(col("user_id").isNotNull()) \
            .filter(col("event_time").isNotNull()) \
            .withColumn("event_type", 
                when(col("raw_payload").isNotNull(), 
                    col("source_system")).otherwise(lit("unknown"))) \
            .withColumn("event_category", 
                lit("default")) \
            .withColumn("properties", 
                lit({})) \
            .withColumn("created_at", col("ingestion_time")) \
            .withColumn("updated_at", current_timestamp()) \
            .select(
                "event_id",
                "event_time",
                "user_id",
                "event_type",
                "event_category",
                "properties",
                "created_at",
                "updated_at"
            )
        
        print(f"   ✅ Transformaciones aplicadas")
        print(f"   📊 Registros después de filtros: {silver_df.count()}")
        
        # Mostrar sample
        print("\n3. Datos de muestra (primeras 5 filas):")
        silver_df.show(5, truncate=False)
        
        # Escribir a Silver
        print("\n4. Escribiendo a silver.events...")
        silver_df.write \
            .mode("append") \
            .format("iceberg") \
            .saveAsTable("silver.events")
        
        print(f"   ✅ Datos escritos exitosamente")
        
        # Verificar
        print("\n5. Verificación:")
        silver_count = spark.table("silver.events").count()
        print(f"   ✅ Total de eventos en silver.events: {silver_count}")
        
        # Estadísticas
        print("\n6. Estadísticas de la capa Silver:")
        stats = spark.sql("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT event_type) as unique_event_types,
                MIN(event_time) as earliest_event,
                MAX(event_time) as latest_event
            FROM silver.events
        """).collect()[0]
        
        print(f"   - Total eventos: {stats[0]}")
        print(f"   - Usuarios únicos: {stats[1]}")
        print(f"   - Tipos de eventos: {stats[2]}")
        print(f"   - Evento más antiguo: {stats[3]}")
        print(f"   - Evento más reciente: {stats[4]}")
        
        # Mostrar distribución por tipo de evento
        print("\n7. Distribución por tipo de evento:")
        spark.sql("""
            SELECT 
                event_type,
                COUNT(*) as count,
                COUNT(DISTINCT user_id) as unique_users
            FROM silver.events
            GROUP BY event_type
            ORDER BY count DESC
        """).show()
        
        print("\n" + "=" * 60)
        print("✅ Transformación completada exitosamente")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en transformación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    try:
        spark = create_spark_session()
        
        # Verificar que la tabla Bronze existe
        try:
            bronze_count = spark.table("bronze.raw_events").count()
            print(f"\n📊 Tabla bronze.raw_events encontrada con {bronze_count} registros")
        except Exception as e:
            print(f"❌ Error: No se encontró la tabla bronze.raw_events")
            print("   Por favor, ejecuta primero los scripts:")
            print("   1. create_iceberg_tables.py")
            print("   2. ingest_bronze_data.py")
            sys.exit(1)
        
        # Ejecutar transformación
        if transform_bronze_to_silver(spark):
            spark.stop()
            sys.exit(0)
        else:
            spark.stop()
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
