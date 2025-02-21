import pika
import json
import requests
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
API_URL = "http://localhost:8080/api/products"

# Conectar a RabbitMQ
params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Crear cola
channel.queue_declare(queue="product_requests", durable=True)

# Obtener datos de la API
response = requests.get(API_URL)
products = response.json() if response.status_code == 200 else []

# Enviar productos a la cola
for product in products:
    message = json.dumps(product)
    channel.basic_publish(exchange="", routing_key="product_requests", body=message)
    print(f"[x] Enviado: {message}")

# Cerrar conexión
connection.close()
