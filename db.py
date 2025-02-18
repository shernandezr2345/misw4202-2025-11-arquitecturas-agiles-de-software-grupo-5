import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_CONFIG = {
    "dbname": os.getenv("DB_NAME", "bd"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASSWORD", "pass"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Función para obtener conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname=DATABASE_CONFIG["dbname"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"]
    )
    return conn