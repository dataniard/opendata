# Issue: Transformación Bronze → Silver

**Title**: Transformar y limpiar datos de Bronze a Silver

**Description**:
Ejecutar `scripts/transform_silver_data.py` para:
- Leer datos de `bronze.raw_events`
- Aplicar limpiezas y validaciones de datos
- Enriquecer con metadatos
- Escribir a `silver.events` y `silver.users`
- Verificar distribución de eventos transformados

**Checklist**:
- [ ] Ejecutar `spark-submit /scripts/transform_silver_data.py`
- [ ] Confirmar datos en silver.events y silver.users
- [ ] Validar calidad de datos transformados
- [ ] Revisar metadatos añadidos

**Labels**: `enhancement`, `data-transformation`
**Milestone**: Pipeline Datos