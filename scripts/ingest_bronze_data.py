#!/usr/bin/env python3
"""
Script de ingestión de datos a capa Bronze
Crea datos de prueba y los ingiere en Iceberg
"""

import random
from datetime import datetime, timedelta
import json
import sys
from config import create_spark_session

def generate_sample_events(num_records=1000):
    """Generar datos de prueba de eventos"""
    print(f"\nGenerando {num_records} eventos de prueba...")
    
    events = []
    source_systems = ["mobile", "web", "api", "backend"]
    
    for i in range(num_records):
        # Generar timestamp aleatorio en los últimos 30 días
        days_back = random.randint(0, 30)
        hours_back = random.randint(0, 23)
        event_time = datetime.now() - timedelta(days=days_back, hours=hours_back)
        
        event = {
            "event_id": f"event_{i:06d}",
            "event_time": event_time,
            "source_system": random.choice(source_systems),
            "user_id": f"user_{random.randint(1, 100):03d}",
            "raw_payload": json.dumps({
                "action": random.choice(["click", "view", "purchase", "share"]),
                "session_id": f"session_{random.randint(1000, 9999)}",
                "duration": random.randint(1, 300)
            }),
            "ingestion_time": datetime.now(),
            "file_name": f"batch_{i // 100:03d}.json"
        }
        events.append(event)
    
    print(f"✅ {num_records} eventos generados")
    return events

def ingest_to_bronze(spark, events):
    """Ingerir eventos a tabla Bronze"""
    print("\nIngiriendo eventos a bronze.raw_events...")
    
    try:
        # Crear DataFrame desde eventos
        df = spark.createDataFrame(events)
        
        # Mostrar schema
        print("\nSchema del DataFrame:")
        df.printSchema()
        
        # Mostrar primeras filas
        print("\nPrimeras 5 filas:")
        df.show(5, truncate=False)
        
        # Ingerir a tabla Iceberg
        df.write \
            .mode("append") \
            .format("iceberg") \
            .saveAsTable("bronze.raw_events")
        
        count = df.count()
        print(f"\n✅ {count} eventos ingiridos exitosamente")
        
        return count
        
    except Exception as e:
        print(f"❌ Error al ingerir datos: {e}")
        return 0

def verify_ingestion(spark, count):
    """Verificar que los datos fueron ingiridos correctamente"""
    print("\nVerificando ingestion...")
    
    try:
        # Verificar conteo total
        total = spark.sql("SELECT COUNT(*) as total FROM bronze.raw_events").collect()[0][0]
        print(f"✅ Total de eventos en bronze.raw_events: {total}")
        
        # Mostrar estadísticas
        stats = spark.sql("""
            SELECT 
                COUNT(DISTINCT source_system) as unique_sources,
                COUNT(DISTINCT user_id) as unique_users,
                MIN(event_time) as earliest_event,
                MAX(event_time) as latest_event
            FROM bronze.raw_events
        """).collect()[0]
        
        print(f"\nEstadísticas:")
        print(f"  - Fuentes únicas: {stats[0]}")
        print(f"  - Usuarios únicos: {stats[1]}")
        print(f"  - Evento más antiguo: {stats[2]}")
        print(f"  - Evento más reciente: {stats[3]}")
        
        # Mostrar datos de ejemplo
        print(f"\nÚltimos 5 eventos ingiridos:")
        spark.sql("""
            SELECT 
                event_id,
                event_time,
                source_system,
                user_id
            FROM bronze.raw_events
            ORDER BY ingestion_time DESC
            LIMIT 5
        """).show(truncate=False)
        
        # Ver snapshots
        print(f"\nSnapshots de bronze.raw_events:")
        spark.sql("""
            SELECT 
                snapshot_id,
                committed_at,
                operation
            FROM bronze.raw_events.snapshots
            ORDER BY committed_at DESC
            LIMIT 5
        """).show()
        
    except Exception as e:
        print(f"⚠️  Error al verificar: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("Ingesta de datos a capa Bronze - OpenData")
    print("=" * 60)
    
    try:
        spark = create_spark_session()
        
        # Generar datos de prueba
        events = generate_sample_events(num_records=1000)
        
        # Ingerir a Bronze
        count = ingest_to_bronze(spark, events)
        
        if count > 0:
            # Verificar ingestion
            verify_ingestion(spark, count)
            
            print("\n" + "=" * 60)
            print("✅ Ingesta completada exitosamente")
            print("=" * 60)
        else:
            print("\n❌ La ingesta falló")
            sys.exit(1)
        
        spark.stop()
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
