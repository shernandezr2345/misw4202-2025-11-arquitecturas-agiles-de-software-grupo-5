FROM maven:3.8.7-eclipse-temurin-11 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY . .
RUN mvn clean package -DskipTests

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=build /app/target/api-gateway-1.0.0.jar api-gateway.jar
EXPOSE 8088
ENTRYPOINT ["java", "-jar", "api-gateway.jar"]