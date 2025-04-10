from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from airflow.providers.http.sensors.http import HttpSensor
import json
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd
import os


project_folder = "/opt/airflow/output/weather_api_project"
os.makedirs(project_folder, exist_ok=True)

def kelvin_to_fahrenheit(temp_in_kelvin):
    """Convierte temperatura de Kelvin a Fahrenheit."""
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit

def kelvin_to_celsius(temp_in_kelvin):
    """Convierte temperatura de Kelvin a Celsius."""
    return temp_in_kelvin - 273.15


def transform_load_data(task_instance):
    """Transforma los datos extraídos de la API del clima y los guarda en un CSV."""
    data = task_instance.xcom_pull(task_ids="extract_weather_data")

    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_celsius = kelvin_to_celsius(data["main"]["temp"])
    feels_like_celsius = kelvin_to_celsius(data["main"]["feels_like"])
    min_temp_celsius = kelvin_to_celsius(data["main"]["temp_min"])
    max_temp_celsius = kelvin_to_celsius(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    # Convertir timestamps de la API a tiempos locales
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    # Estructura de datos transformados
    transformed_data = {
        "City": city,
        "Description": weather_description,
        "Temperature (C)": round(temp_celsius, 2),
        "Feels Like (C)": round(feels_like_celsius, 2),
        "Minimum Temp (C)": round(min_temp_celsius, 2),
        "Maximum Temp (C)": round(max_temp_celsius, 2),
        "Pressure": pressure,
        "Humidity": humidity,
        "Wind Speed": wind_speed,
        "Time of Record": time_of_record,
        "Sunrise (Local Time)": sunrise_time,
        "Sunset (Local Time)": sunset_time                        
    }

    # Convertir a DataFrame y guardar en CSV
    df_data = pd.DataFrame([transformed_data])
    now = datetime.now().strftime("%d%m%Y%H%M%S")
    filename = os.path.join(project_folder, f"current_weather_data_portland_{now}.csv")
    #filename = f"/opt/airflow/output/weather_api_project/current_weather_data_portland_{now}.csv"
    df_data.to_csv(filename, index=False)


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

        extract_weather_data = SimpleHttpOperator(
            task_id = 'extract_weather_data',
            http_conn_id = 'weathermap_api',
            endpoint='data/2.5/weather?q=Portland&appid=ebbdd1fccf92a15decee15eb9e13c1cc',
            method='GET',
            response_filter = lambda r: json.loads(r.text),
            log_response=True
        )

        transform_load_weather_data = PythonOperator(
            task_id='transform_load_weather_data',
            python_callable=transform_load_data
        )



        is_weather_api_ready >> extract_weather_data >> transform_load_weather_data








