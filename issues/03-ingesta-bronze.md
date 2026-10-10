# Issue: Ingesta de datos Bronze

**Title**: Ingestar datos de prueba a capa Bronze

**Description**:
Ejecutar `scripts/ingest_bronze_data.py` para ingerir 1000 eventos de prueba:
- Generar datos de prueba con Spark Session configurada con Iceberg
- Ingestar a tabla `bronze.raw_events`
- Verificar datos y snapshots creados
- Mostrar estadísticas de los datos ingeridos

**Checklist**:
- [ ] Ejecutar `spark-submit /scripts/ingest_bronze_data.py`
- [ ] Confirmar 1000 registros en bronze.raw_events
- [ ] Verificar snapshots de Iceberg
- [ ] Revisar estadísticas de salida

**Labels**: `enhancement`, `data-ingestion`
**Milestone**: Pipeline Datos