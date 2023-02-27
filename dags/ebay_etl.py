from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

from scripts import ebay_extract_price
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 2, 10),
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': False,
}

with DAG(
    default_args=default_args,
    dag_id='etl_ebay_gpu_avg',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    check_table = PostgresOperator(
        task_id="check_table_exists",
        sql="""
            CREATE TABLE IF NOT EXISTS rtx_3000_gpu_prices (
            date DATE PRIMARY KEY,
            rtx_3050 DECIMAL(6,2) NOT NULL,
            rtx_3060 DECIMAL(6,2) NOT NULL,
            rtx_3060_ti DECIMAL(6,2) NOT NULL,
            rtx_3070 DECIMAL(6,2) NOT NULL,
            rtx_3070_ti DECIMAL(6,2) NOT NULL,
            rtx_3080 DECIMAL(6,2) NOT NULL,
            rtx_3080_ti DECIMAL(6,2) NOT NULL,
            rtx_3090 DECIMAL(6,2) NOT NULL,
            rtx_3090_ti DECIMAL(6,2) NOT NULL);
          """,
    )

    @task
    def gpu_search(x: str):
        return ebay_extract_price.get_average(x)

    @task
    def get_nvidia_statement(data):
        values = list(data)
        today = datetime.today().strftime('%Y-%m-%d')

        values.insert(0, today)

        formatted_values = tuple(values)
        query = f'INSERT INTO rtx_3000_gpu_prices VALUES {formatted_values}'

        return query

    @task
    def load_to_postgres(query):
        hook = PostgresHook(postgres_conn_id="postgres_default")
        hook.run(query)


    rtx_3000 = gpu_search.expand(x=['RTX 3050 gpu',
                                    'RTX 3060 gpu',
                                    'RTX 3060 ti gpu',
                                    'RTX 3070 gpu',
                                    'RTX 3070 Ti gpu',
                                    'RTX 3080 gpu',
                                    'RTX 3080 Ti gpu',
                                    'RTX 3090 gpu',
                                    'RTX 3090 Ti gpu',
                                    ])

    data = get_nvidia_statement(rtx_3000)

    check_table >> load_to_postgres(data)

