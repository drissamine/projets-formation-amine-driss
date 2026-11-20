from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    "owner": "Tesnim",
    "retries": 5,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="our_first_dag_",
    default_args=default_args,
    description="This is our first dag that we write",
    start_date=datetime(2025, 4, 14, 2),
    schedule="@daily",
) as dag:
    task1 = BashOperator(
        task_id="first_task",
        bash_command="echo bonjour, ceci est le premier task!",
    )

    task2 = BashOperator(
        task_id="second_task",
        bash_command="echo bonjour, je suis task2 et je mexécute aprés task1",
    )

    task3 = BashOperator(
        task_id="thrid_task",
        bash_command="echo bonjour, je suis task3 et je mexécute après task1 au même instant que task2!",
    )

    task1 >> [task2, task3]
