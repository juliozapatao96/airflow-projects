from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from airflow.providers.http.sensors.http import HttpSensor
import json

default_args = {
    'owner':'airflow',
    'depends_on_past':False,
    'start_date':datetime(2023, 1, 8),
    'email':['myemail@domain.com'],
    'email_on_failure':False,
    'email_on_retry':False,
    'retries':2,
    'retry_delay':timedelta(minutes=2)
}

with DAG('weather_dag',
        default_args = default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:

        is_weather_api_ready = HttpSensor(
            task_id = 'is_weather_api_ready',
            http_conn_id='weathermap_api', # Se crea esta conexión en airflow en Admin -> Connections
            endpoint='data/2.5/weather?q=Portland&appid=ebbdd1fccf92a15decee15eb9e13c1cc'
        )








