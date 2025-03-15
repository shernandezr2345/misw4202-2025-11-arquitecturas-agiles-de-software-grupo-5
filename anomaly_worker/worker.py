import pika
import json
import requests
import time
import threading
from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

# Configuración del servidor Flask para métricas
app = Flask(__name__)
ANOMALY_COUNT = Counter("anomaly_requests", "Número de anomalías detectadas")

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

def start_http_server():
    """Levanta el servidor Flask en un hilo separado"""
    app.run(host="0.0.0.0", port=8001)

def connect_to_rabbitmq(max_retries=10, delay=5):
    """Intenta conectarse a RabbitMQ con reintentos en caso de fallo"""
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            print("Conexión establecida con RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Intento {i+1}/{max_retries}: No se pudo conectar a RabbitMQ. Reintentando en {delay} segundos...")
            time.sleep(delay)
    raise Exception("No se pudo conectar a RabbitMQ después de varios intentos.")

def consume_anomalies():
    """Consume mensajes de la cola RabbitMQ y actualiza la métrica"""
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    
    channel.queue_declare(queue="anomaly_requests", durable=True)

    def callback(ch, method, properties, body):
        print(f"[x] Recibido: {body.decode()}")
        ANOMALY_COUNT.inc()  # Incrementa la métrica en Prometheus
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="anomaly_requests", on_message_callback=callback)
    print("[*] Esperando mensajes. Para salir presiona CTRL+C")
    channel.start_consuming()

# Iniciar el servidor Flask en un hilo
threading.Thread(target=start_http_server, daemon=True).start()

# Iniciar el consumidor de RabbitMQ
consume_anomalies()
