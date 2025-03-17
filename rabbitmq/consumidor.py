import pika
import json
import requests
import time
import sqlite3
import threading

MAX_RETRIES = 10  # Número máximo de intentos de conexión

def connect_to_rabbitmq():
    """ Intenta conectarse a RabbitMQ con reintentos en caso de fallo """
    for i in range(MAX_RETRIES):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            print("Conexión establecida con RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Intento {i+1}/{MAX_RETRIES}: No se pudo conectar a RabbitMQ. Reintentando en 5 segundos...")
            time.sleep(5)  # Espera antes de volver a intentar
    raise Exception("No se pudo conectar a RabbitMQ después de varios intentos.")

def detect_anomaly(product_data):
    """ Lógica para detectar anomalías en los productos """
    product_valor = product_data.get("price", 0)
    print(f"⚠️ VAlloorooror: {product_valor}'.")

    if product_data.get("price", 0) < 1:  # Ejemplo: precio extremadamente bajo
        return True
    if product_data.get("stock", 0) < 0:  # Ejemplo: stock negativo
        return True
    return False

def callback(ch, method, properties, body):
    """ Procesa los mensajes recibidos desde RabbitMQ y envía el resultado a otra cola """
    try:
        message = json.loads(body)
        product_id = message.get("product_id")  # Extrae el ID del producto
        blocked_ip = message.get("ip_address")  # Extrae la IP bloqueada

        if product_id:
            print(f"🔍 Consultando producto {product_id}...")
            # time.sleep(5)
            # Hacer la consulta HTTP a la API de productos
            url = f"http://flask_api:8080/api/products/{product_id}"
            response = requests.get(url)
            
            print(f"🔍 Resultado {response.status_code}...")
            # Preparar el resultado para la cola de respuestas
            if response.status_code == 200:
                product_data = response.json()

                if detect_anomaly(product_data):
                    anomaly_message = {
                        "tabla": "products",
                        "id": product_id,
                        "status": "anomaly_requests",
                        "data": product_data
                    }
                    anomaly_channel.basic_publish(
                        exchange='',
                        routing_key='anomaly_requests',
                        body=json.dumps(anomaly_message),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    print(f"⚠️ Anomalía detectada en producto {product_id}, enviado a la cola 'anomaly_requests'.")

                    if blocked_ip:
                        blocked_ip_message = {
                            "ip_address": blocked_ip
                        }
                        anomaly_channel.basic_publish(
                            exchange='',
                            routing_key='blocked_ips',
                            body=json.dumps(blocked_ip_message),
                            properties=pika.BasicProperties(delivery_mode=2)
                        )
                        print(f"🚫 IP {blocked_ip} bloqueada, enviado a la cola 'blocked_ips'.")
                    return  # No procesamos el mensaje en la cola normal si es anómalo
        
                result = {
                    "product_id": product_id,
                    "status": "success",
                    "data": response.json()
                }
                print(f"Producto encontrado: {response.json()}")
            else:
                result = {
                    "product_id": product_id,
                    "status": "error",
                    "message": f"No se encontró el producto {product_id}."
                }
                print(f"Error {response.status_code}: No se encontró el producto {product_id}")

        else:
            result = {
                "status": "error",
                "message": "No se encontró 'product_id' en el mensaje."
            }
            print("Error: No se encontró 'product_id' en el mensaje")

        # Publicar la respuesta en otra cola
        response_channel.basic_publish(
            exchange='',
            routing_key='product_responses',
            body=json.dumps(result),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hace el mensaje persistente
            )
        )
        print(f"Resultado enviado a la cola 'product_responses'.")

    except json.JSONDecodeError:
        print("Error: No se pudo decodificar el mensaje JSON recibido.")

def blocked_ips_callback(ch, method, properties, body):
    """ Procesa los mensajes de la cola 'blocked_ips' y almacena la IP en la base de datos """
    try:
        message = json.loads(body)
        ip_address = message.get("ip_address")

        if ip_address:
            print(f"Dirección IP bloqueada detectada: {ip_address}")
            save_blocked_ip(ip_address)  # Guardar en la base de datos
        else:
            print("Error: No se encontró 'ip_address' en el mensaje")

    except json.JSONDecodeError:
        print("Error: No se pudo decodificar el mensaje JSON recibido.")

# Conectar a RabbitMQ con reintentos
connection = connect_to_rabbitmq()
channel = connection.channel()

# Declarar las colas
channel.queue_declare(queue="product_requests", durable=True)
response_channel = connection.channel()
response_channel.queue_declare(queue="product_responses", durable=True)

# Nueva cola para anomalías
anomaly_channel = connection.channel()
anomaly_channel.queue_declare(queue="anomaly_requests", durable=True)

# Registrar consumidores para ambas colas en el mismo canal
channel.basic_consume(queue='product_requests', on_message_callback=callback, auto_ack=True)

print("📡 Esperando mensajes de RabbitMQ...")

# Iniciar la escucha de eventos para ambas colas
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("🛑 Deteniendo el consumidor...")
    channel.stop_consuming()