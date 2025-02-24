import pika
import json
import requests
import time

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

def callback(ch, method, properties, body):
    """ Procesa los mensajes recibidos desde RabbitMQ y envía el resultado a otra cola """
    try:
        message = json.loads(body)
        product_id = message.get("product_id")  # Extrae el ID del producto

        if product_id:
            print(f"🔍 Consultando producto {product_id}...")
            # time.sleep(5)
            # Hacer la consulta HTTP a la API de productos
            url = f"http://flask_api:8080/api/products/{product_id}"
            response = requests.get(url)

            # Preparar el resultado para la cola de respuestas
            if response.status_code == 200:
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

# Conectar a RabbitMQ con reintentos
connection = connect_to_rabbitmq()
channel = connection.channel()

# Declarar las colas
channel.queue_declare(queue="product_requests", durable=True)
response_channel = connection.channel()
response_channel.queue_declare(queue="product_responses", durable=True)

# Escuchar mensajes
channel.basic_consume(queue='product_requests', on_message_callback=callback, auto_ack=True)

print("📡 Esperando mensajes de RabbitMQ...")
channel.start_consuming()
