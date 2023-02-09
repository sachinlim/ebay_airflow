from airflow import DAG
from airflow.decorators import task

from scripts import ebay_extract_price
from datetime import datetime


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 2, 1),
    'depends_on_past': False,
}

with DAG(
    default_args=default_args,
    dag_id='xcom_dag',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    @task
    def gpu_search(x: str):
        return ebay_extract_price.get_average(x)

    @task
    def load(rtx_3000, rtx_2000):
        print('RTX 3000 values: ', rtx_3000)
        print('RTX 2000 values: ', rtx_2000)

    rtx_3000 = gpu_search.expand(x=['RTX 3050', 'RTX 3060', 'RTX 3060 ti', 'RTX 3070', 'RTX 3070 Ti', 'RTX 3080', 'RTX 3080 Ti', 'RTX 3090', 'RTX 3090 Ti'])
    rtx_2000 = gpu_search.expand(x=['RTX 2060', 'RTX 2060 Super', 'RTX 2070', 'RTX 2070 Super', 'RTX 2080', 'RTX 2080 Super', 'RTX 2080 Ti'])

    load(rtx_3000, rtx_2000)
