# Issue: Crear tablas Iceberg

**Title**: Crear nombrespaces y tablas medallion Iceberg

**Description**:
Ejecutar `scripts/create_iceberg_tables.py` para crear:
- Namespaces: bronze, silver, gold
- Tablas Bronze: raw_events, raw_logs
- Tablas Silver: events, users
- Tablas Gold: daily_user_metrics, event_types_daily

Configuración de particionado y compresión para cada tabla.

**Checklist**:
- [ ] Ejecutar `spark-submit /scripts/create_iceberg_tables.py`
- [ ] Verificar creación de namespaces en Hive Metastore
- [ ] Confirmar creación de todas las tablas
- [ ] Revisar metadatos en PostgreSQL

**Labels**: `enhancement`, `iceberg`
**Milestone**: Pipeline Datos