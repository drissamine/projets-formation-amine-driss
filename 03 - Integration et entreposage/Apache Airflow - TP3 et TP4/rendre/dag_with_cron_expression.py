from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    "owner": "Tesnim",
    "retries": 5,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dag_with_cron_expression",
    default_args=default_args,
    start_date=datetime(2021, 11, 1),
    schedule="0 3 * * Tue-Fri",
) as dag:
    task1 = BashOperator(
        task_id="task1",
        bash_command="echo dag with cron expression!",
    )
