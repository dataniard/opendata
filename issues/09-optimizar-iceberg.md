# Issue: Optimizar tablas Iceberg

**Title**: Optimizar tablas Iceberg Gold para performance de queries

**Description**:
Añadir optimizaciones a las tablas Gold layer:
- Índices sobre columnas de consulta frecuente
- Sort orders para particionamiento órdeno
- Políticas de compaction automático
- Configuración de TTL/retención de datos
- Z-ordering para columnas de filtrado común

**Checklist**:
- [ ] Añadir índices a `gold.daily_user_metrics`
- [ ] Añadir índices a `gold.event_types_daily`
- [ ] Configurar sort orders en todas tablas Gold
- [ ] Ejecutar compaction manual
- [ ] Verificar mejora en performance de queries

**Labels**: `enhancement`, `performance`, `iceberg`
**Milestone**: Optimización