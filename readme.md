# Experimento: Evaluación de Tácticas de Disponibilidad en el Componente de Consulta de Productos

## Objetivo

El objetivo de este experimento es evaluar la efectividad de la táctica de monitoreo activo en un sistema basado en Flask, utilizando un componente de Consulta de Productos con procesamiento asíncrono.

El experimento se llevará a cabo mediante la simulación de una carga elevada de solicitudes de consulta de productos, con el fin de evaluar la disponibilidad y resiliencia del sistema. Además, se analizará cómo el monitoreo activo contribuye a la detección temprana de problemas, evitando que afecten la disponibilidad del servicio y asegurando que el componente se mantenga operativo bajo alta carga y posibles fallos.

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

### 4. RabbitMQ

Carpeta: rabbitmq

Utilizado para la gestión de colas de mensajería y el procesamiento asíncrono de las consultas de productos.

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

