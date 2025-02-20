Levantar contenedor

docker-compose up -d --build

Migraciones:

1. docker exec -it flask_api flask db init
2. docker exec -it flask_api flask db migrate -m "Crear tabla products"
3. docker exec -it flask_api flask db upgrade


Acceder a swagger 

http://localhost:8080/swagger