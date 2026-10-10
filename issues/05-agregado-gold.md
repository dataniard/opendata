# Issue: Agregado a capa Gold

**Title**: Agregar datos a capa Gold (serving)

**Description**:
Ejecutar `scripts/aggregate_gold_data.py` para crear:
- `gold.daily_user_metrics`: métricas diarias por usuario
- `gold.event_types_daily`: agregaciones por tipo de evento
- Verificar integridad de datos
- Mostrar top usuarios y distribución

**Checklist**:
- [ ] Ejecutar `spark-submit /scripts/aggregate_gold_data.py`
- [ ] Confirmar creación de tablas Gold
- [ ] Verificar integridad de métricas
- [ ] Revisar datos de top usuarios

**Labels**: `enhancement`, `data-aggregation`
**Milestone**: Pipeline Datos