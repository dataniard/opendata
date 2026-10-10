# Issue: Configurar Airflow DAGs

**Title**: Implementar DAGs de Airflow para orquestación ETL

**Description**:
Desarrollar el DAG de ejemplo en `docker/airflow/dags/opendata_example_dag.py`:
- DAG `opendata_etl_pipeline` para scheduling diario
- Ejecutar `run_etl_pipeline.sh` dentro del pipeline
- Permitir monitorización desde la UI de Airflow (puerto 8085)
- Configurar retries y alerts

**Checklist**:
- [ ] Crear/actualizar DAG en `docker/airflow/dags/opendata_example_dag.py`
- [ ] Desplegar Airflow con `docker compose up -d airflow-webserver`
- [ ] Acceder a UI Airflow en http://localhost:8085
- [ ] Ejecutar DAG `opendata_etl_pipeline`
- [ ] Verificar scheduling diario y retries

**Labels**: `enhancement`, `airflow`
**Milestone**: Integración ETL