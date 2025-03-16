# Experimento: Evaluación de Tácticas de SEGURIDAD en el Componente de Consulta de Productos (DETECCIÒN)



## Objetivo

El objetivo de este experimento es la capacidad del sistema para identificar accesos no autorizados o eventos anómalos y generar alertas en tiempo real. El escenario de prueba incluirá intentos de acceso por parte de un usuario fraudulento que intente ingresar sin autenticación o desde una dirección IP sospechosa o detectar eventos que puedan ser sospechos, lo que debería desencadenar una respuesta automática del sistema. Los resultados esperados incluyen la detección efectiva de estos intentos de acceso, la generación de alertas en tiempo real a través de RabbitMQ, el registro y visualización de los eventos de seguridad, y la demostración de una acción de respuesta ante el intento de intrusión, como el envío de una notificación o el bloqueo del acceso.​ 


![image](https://github.com/user-attachments/assets/7259121a-ac37-4818-a084-c217fb059032)

## Componentes del Proyecto

### 1. Flask API

Carpeta: componenteProducto

Endpoints:
- GET /api/products - Consultar todos los productos
- GET /api/products/{id} - Consultar un producto por ID específico

Documentación de la API:
- Accede a Swagger en: http://localhost:8080/swagger

### 2. JMeter

Carpeta: JmeterProducto

Utilizado para simular la carga elevada de solicitudes y realizar pruebas de rendimiento.

### 3. Prometheus

Carpeta: prometheus

Configurado para monitorear métricas del sistema y enviar alertas ante posibles problemas.

scrape_configs:
  - job_name: 'flask_api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['flask_api:8080']

  - job_name: 'anomaly_worker'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['anomaly_worker:8001']


### 4. RabbitMQ

Carpeta: rabbitmq

Utilizado para la gestión de colas de mensajería y el procesamiento asíncrono de las consultas de productos.

### 5. Zuul - apigateway

Carpeta: zuul

El Gateway gestiona el enrutamiento, permitiendo un punto de acceso unificado a los servicios

- URL directa: http://localhost:8080/
- URL a través del gateway: http://localhost:8088/flask/

### 6. Anomaly Worker (anomaly_worker)
Función: Analiza métricas de productos en búsqueda de anomalías.

Endpoint de métricas:

GET http://localhost:8001/metrics
Métricas principales:

anomaly_requests_total → Total de anomalías detectadas.




## Cómo Levantar el Proyecto

Para iniciar todos los servicios del proyecto en contenedores Docker, ejecuta el siguiente comando en la raíz del proyecto:

```
docker-compose up -d --build
```

Esto iniciará todos los contenedores en segundo plano (-d) y reconstruirá las imágenes si es necesario (--build).

## Configuración de la Base de Datos (Migraciones)

Para crear la base de datos del API Flask, sigue estos pasos:

1. Inicializar las migraciones:
```
docker exec -it flask_api flask db init
```

2. Crear las migraciones para la tabla products:
```
docker exec -it flask_api flask db migrate -m "Crear tabla products"
```

3. Aplicar las migraciones (crear la tabla en la base de datos):
```
docker exec -it flask_api flask db upgrade
```

# Monitorización con Prometheus y Grafana

Asegúrate de tener **Docker** y **Docker Compose** instalados y levantar los contenedores

```yaml
docker-compose up -d
```

### Acceder a Prometheus

Una vez que Prometheus está corriendo, accede a su interfaz web:

```
http://localhost:9090
```

#### Consultas en PromQL

Puedes realizar consultas en la pestaña **Graph** de Prometheus. Ejemplos de queries:

- **Total de requests:**
  ```
  http_requests_total
  ```
- **Requests por método HTTP:**
  ```
  http_requests_total{method="GET"}
  ```
- **Tiempo de respuesta promedio:**
  ```
  rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
  ```

---

### Acceder a Grafana

Abre Grafana en tu navegador:

```
http://localhost:3000
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin`

#### Agregar Prometheus como Data Source

1. Ve a **Configuration** → **Data Sources**.
2. Selecciona **Add data source** → **Prometheus**.
3. En la URL coloca:
   ```
   http://prometheus:9090
   ```
4. Guarda la configuración.

#### Crear un Dashboard en Grafana

1. Ve a **Create** → **Dashboard**.
2. Agrega un **Panel**.
3. En **Query**, selecciona `Prometheus` como Data Source y usa esta consulta:
   ```
   http_requests_total{method="GET"}
   ```
4. Guarda el dashboard.

---

Con esta configuración, puedes visualizar métricas en tiempo real y analizar el rendimiento de tu aplicación Flask usando **Prometheus y Grafana**.


## Consideraciones Adicionales

- Asegúrate de tener Docker y Docker Compose instalados en tu sistema antes de iniciar.
- Verifica que los puertos necesarios (por ejemplo, 8080 para Swagger) no estén en uso para evitar conflictos.
- Para detener los contenedores, ejecuta:

```
docker-compose down
```

