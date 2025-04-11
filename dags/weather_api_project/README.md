## 📊 Weather ETL Pipeline with Airflow & S3

Este proyecto es un pipeline de ETL que extrae datos meteorológicos de la API de OpenWeather, los transforma y los guarda como archivos `.csv` que se almacenan en un bucket de S3. El pipeline corre diariamente usando Apache Airflow y está contenido dentro de Docker.

---

### 🚀 Estructura del pipeline

```bash

weather_dag/
├── dags/
│   └── weather_dag.py          # DAG principal de Airflow
├── docker-compose.yml          # Orquestación con Docker
├── output/                     # Archivos locales generados (luego subidos a S3)
├── plugins/                    # (opcional) Plugins de Airflow
└── README.md

```

---

### 🔁 Flujo de tareas

1. **Check API**: Verifica que la API de OpenWeather esté disponible.
2. **Extract**: Hace un GET a la API para obtener los datos del clima actual en Portland.
3. **Transform & Load (local)**: Transforma los datos crudos y los guarda como `.csv` localmente.
4. **Upload to S3**: Sube ese archivo a un bucket de S3, en la carpeta `weather-data/`.

---

### 💾 Ejemplo de archivo CSV generado

```

City,Description,Temperature (C),Feels Like (C),Minimum Temp (C),Maximum Temp (C),Pressure,Humidity,Wind Speed,Time of Record,Sunrise (Local Time),Sunset (Local Time)
Portland,clear sky,16.2,15.5,14.3,17.9,1013,45,3.2,2025-04-09 08:22:00,2025-04-09 06:45:00,2025-04-09 19:55:00

```

---

### ⚙️ Requisitos

- Docker & Docker Compose
- Airflow (ejecutándose con `docker-compose`)
- Cuenta de AWS con un bucket S3 (`s3-jz-weather`)
- API Key de OpenWeather

---

### 🔐 Configuración de Airflow

### 📍 Conexiones necesarias (en Admin > Connections):

- **`weathermap_api`**
    - Type: HTTP
    - Host: `https://api.openweathermap.org/`
- **`aws_default`**
    - Type: Amazon Web Services
    - Access Key ID / Secret Access Key

---

### 🐳 Cómo levantar el entorno

```bash

# Inicializar servicios
docker-compose up airflow-init

# Correr todos los contenedores
docker-compose up

```

Airflow estará disponible en: http://localhost:8080

Usuario por defecto: `airflow` / Contraseña: `airflow`

---

### 📤 Subida a S3

Los archivos generados se suben a:

```

s3://s3-jz-weather/weather-data/current_weather_data_portland_<timestamp>.csv

```

Puedes revisar el contenido directamente desde AWS Console o usando la AWS CLI.

---


### 📌 Pendientes / Ideas futuras

- [ ]  Enviar notificación por correo o Slack cuando se suba el archivo.
- [ ]  Agregar más ciudades como parámetros.
- [ ]  Crear una visualización diaria en un dashboard (ej: Superset, Looker).
- [ ]  Configurar el DAG para múltiples entornos (dev, staging, prod).
