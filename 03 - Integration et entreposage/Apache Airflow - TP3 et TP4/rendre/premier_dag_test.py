from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    "owner": "Tesnim",
    "depends_on_past": False,
    "start_date": datetime(2025, 4, 14),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    "premier_dag_test",
    default_args=default_args,
    description="mon premier dag",
    schedule=timedelta(days=1),
)


def print_hello():
    return "hello workd, c'est mon premier dag"


start = EmptyOperator(task_id="start", dag=dag)

hello_world = PythonOperator(
    task_id="hello_world",
    python_callable=print_hello,
    dag=dag,
)

end = EmptyOperator(task_id="end", dag=dag)

start >> hello_world >> end
