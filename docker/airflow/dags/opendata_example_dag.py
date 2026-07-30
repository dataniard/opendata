from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

with DAG(
    dag_id='opendata_etl_pipeline',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['opendata'],
) as dag:

    run_etl_pipeline = BashOperator(
        task_id='run_etl_pipeline',
        bash_command='bash /opt/airflow/scripts/run_etl_pipeline.sh',
    )

    run_etl_pipeline
