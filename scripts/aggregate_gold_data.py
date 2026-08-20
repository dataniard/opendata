#!/usr/bin/env python3
"""
Script de agregación: Silver → Gold
Crea agregaciones de datos optimizadas para consumo analítico
"""

from pyspark.sql.functions import col, count, countDistinct, min, max, to_date, current_timestamp, lit, when
from datetime import datetime
import sys
from config import create_spark_session

def aggregate_daily_metrics(spark):
    """Crear agregación diaria de métricas por usuario"""
    print("\n" + "=" * 60)
    print("Agregación 1: Métricas Diarias por Usuario")
    print("=" * 60)
    
    try:
        print("\n1. Leyendo datos de silver.events...")
        silver_df = spark.table("silver.events")
        print(f"   ✅ {silver_df.count()} registros leídos")
        
        print("\n2. Calculando agregaciones diarias...")
        gold_df = silver_df \
            .withColumn("date", to_date(col("event_time"))) \
            .groupBy("date", "user_id") \
            .agg(
                count("event_id").alias("total_events"),
                countDistinct("event_type").alias("unique_event_types"),
                min("event_time").alias("first_event_time"),
                max("event_time").alias("last_event_time")
            ) \
            .withColumn("created_at", current_timestamp())
        
        print(f"   ✅ {gold_df.count()} registros agregados")
        
        print("\n3. Datos de muestra:")
        gold_df.show(5, truncate=False)
        
        print("\n4. Escribiendo a gold.daily_user_metrics...")
        gold_df.write \
            .mode("append") \
            .format("iceberg") \
            .saveAsTable("gold.daily_user_metrics")
        
        print(f"   ✅ Datos escritos exitosamente")
        
        # Verificar
        gold_count = spark.table("gold.daily_user_metrics").count()
        print(f"   📊 Total de registros en gold.daily_user_metrics: {gold_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def aggregate_event_types_daily(spark):
    """Crear agregación diaria de eventos por tipo"""
    print("\n" + "=" * 60)
    print("Agregación 2: Eventos Diarios por Tipo")
    print("=" * 60)
    
    try:
        print("\n1. Leyendo datos de silver.events...")
        silver_df = spark.table("silver.events")
        
        print("\n2. Calculando agregaciones por tipo de evento...")
        gold_df = silver_df \
            .withColumn("date", to_date(col("event_time"))) \
            .groupBy("date", "event_type") \
            .agg(
                count("event_id").alias("event_count"),
                countDistinct("user_id").alias("unique_users")
            ) \
            .withColumn("created_at", current_timestamp())
        
        print(f"   ✅ {gold_df.count()} registros agregados")
        
        print("\n3. Datos de muestra:")
        gold_df.show(5, truncate=False)
        
        print("\n4. Escribiendo a gold.event_types_daily...")
        gold_df.write \
            .mode("append") \
            .format("iceberg") \
            .saveAsTable("gold.event_types_daily")
        
        print(f"   ✅ Datos escritos exitosamente")
        
        # Verificar
        gold_count = spark.table("gold.event_types_daily").count()
        print(f"   📊 Total de registros en gold.event_types_daily: {gold_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_gold_layer(spark):
    """Verificar la integridad de la capa Gold"""
    print("\n" + "=" * 60)
    print("Verificación de Capa Gold")
    print("=" * 60)
    
    try:
        print("\n1. Estadísticas globales de gold.daily_user_metrics:")
        spark.sql("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT date) as unique_dates,
                COUNT(DISTINCT user_id) as unique_users,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                CAST(AVG(total_events) AS INT) as avg_events_per_user_day,
                MAX(total_events) as max_events_in_a_day
            FROM gold.daily_user_metrics
        """).show(truncate=False)
        
        print("\n2. Top 10 usuarios por eventos totales:")
        spark.sql("""
            SELECT 
                user_id,
                SUM(total_events) as total_events,
                COUNT(DISTINCT date) as active_days,
                CAST(AVG(total_events) AS INT) as avg_events_per_day
            FROM gold.daily_user_metrics
            GROUP BY user_id
            ORDER BY total_events DESC
            LIMIT 10
        """).show(truncate=False)
        
        print("\n3. Distribución de eventos por tipo:")
        spark.sql("""
            SELECT 
                event_type,
                SUM(event_count) as total_events,
                COUNT(DISTINCT date) as days_with_events,
                CAST(AVG(unique_users) AS INT) as avg_unique_users
            FROM gold.event_types_daily
            GROUP BY event_type
            ORDER BY total_events DESC
        """).show(truncate=False)
        
        print("\n4. Snapshots de tablas Gold:")
        spark.sql("""
            SELECT 
                snapshot_id,
                committed_at,
                operation
            FROM gold.daily_user_metrics.snapshots
            ORDER BY committed_at DESC
            LIMIT 5
        """).show()
        
        print("\n✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"⚠️  Advertencia en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("AGREGACIÓN: Silver → Gold")
    print("=" * 60)
    
    try:
        spark = create_spark_session()
        
        # Verificar que la tabla Silver existe
        try:
            silver_count = spark.table("silver.events").count()
            print(f"\n📊 Tabla silver.events encontrada con {silver_count} registros")
        except Exception as e:
            print(f"❌ Error: No se encontró la tabla silver.events")
            print("   Por favor, ejecuta primero los scripts:")
            print("   1. create_iceberg_tables.py")
            print("   2. ingest_bronze_data.py")
            print("   3. transform_silver_data.py")
            sys.exit(1)
        
        # Ejecutar agregaciones
        success = True
        
        if not aggregate_daily_metrics(spark):
            success = False
        
        if not aggregate_event_types_daily(spark):
            success = False
        
        # Verificar integridad
        if not verify_gold_layer(spark):
            print("\n⚠️  Algunas verificaciones fallaron, pero los datos pueden estar disponibles")
        
        spark.stop()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ AGREGACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print("\nTus datos están listos en la capa Gold para:")
            print("  - Consultas analíticas")
            print("  - Dashboards en Superset/Metabase")
            print("  - Reportes de BI")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
