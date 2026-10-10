# Issue: Validaciones de calidad de datos

**Title**: Implementar validaciones de calidad de datos across layers

**Description**:
Añadir checks de calidad de datos en todas las capas medallion:
- Conteos de registros por tabla
- Porcentaje de valores nulos
- Validación de esquema esperado
- Checks de consistencia entre Bronze/Silver/Gold
- Reportes de calidad automatizados

**Checklist**:
- [ ] Implementar validaciones en `scripts/create_iceberg_tables.py`
- [ ] Añadir checks en `ingest_bronze_data.py`
- [ ] Agregar validaciones en `transform_silver_data.py`
- [ ] Incluir checks en `aggregate_gold_data.py`
- [ ] Crear reporte automático de calidad

**Labels**: `enhancement`, `quality`, `data-quality`
**Milestone**: Validación