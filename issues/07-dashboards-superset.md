# Issue: Crear dashboards Superset

**Title**: Construir dashboards BI conectados a capa Gold

**Description**:
Conectar Superset (puerto 8088) a las tablas Gold layer:
- `gold.daily_user_metrics`
- `gold.event_types_daily`
- Crear visualizaciones de:
  - Métricas por usuario a lo largo del tiempo
  - Distribución de tipos de eventos
  - Top usuarios activos
- Guardar dashboards para consumo analítico

**Checklist**:
- [ ] Acceder a Superset en http://localhost:8088
- [ ] Conectar a la base de datos PostgreSQL/Hive Metastore
- [ ] Crear conexión Iceberg/Tables
- [ ] Construir 3+ dashboards con datos Gold
- [ ] Guardar y compartir dashboards

**Labels**: `enhancement`, `bi`, `visualization`
**Milestone**: Visualización