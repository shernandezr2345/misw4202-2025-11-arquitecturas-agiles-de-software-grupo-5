package com.gateway;

import com.netflix.zuul.ZuulFilter;
import com.netflix.zuul.context.RequestContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class AuthenticationLoggingFilter extends ZuulFilter {

    private static final Logger logger = LoggerFactory.getLogger(AuthenticationLoggingFilter.class);

    private final Map<String, Integer> failedAttempts = new ConcurrentHashMap<>();
    private final Map<String, LocalDateTime> blockedIps = new ConcurrentHashMap<>();

    private static final int MAX_FAILED_ATTEMPTS = 15;
    private static final long BLOCK_TIME_IN_MINUTES = 1;

    private static final String RABBITMQ_URL = System.getenv("RABBITMQ_URL");
    private static final String DEFAULT_RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/";
    private static final String QUEUE_NAME = "anomaly_requests";

    @Override
    public String filterType() {
        return "post";
    }

    @Override
    public int filterOrder() {
        return 1;
    }

    @Override
    public boolean shouldFilter() {
        return true;
    }

    @Override
    public Object run() {
        RequestContext ctx = RequestContext.getCurrentContext();
        HttpServletRequest request = ctx.getRequest();
        HttpServletResponse response = ctx.getResponse();
        String clientIp = request.getRemoteAddr();

        if (blockedIps.containsKey(clientIp)) {
            LocalDateTime blockTime = blockedIps.get(clientIp);
            if (blockTime.plusMinutes(BLOCK_TIME_IN_MINUTES).isAfter(LocalDateTime.now())) {
                ctx.setSendZuulResponse(false);
                ctx.setResponseStatusCode(403);
                ctx.setResponseBody("IP bloqueada temporalmente por múltiples intentos fallidos.");
                logger.warn("Bloqueo de IP {} por múltiples intentos fallidos", clientIp);
                sendBlockedIpToQueue(clientIp);
                return null;
            } else {
                blockedIps.remove(clientIp);
                failedAttempts.remove(clientIp);
            }
        }

        if (response.getStatus() == HttpServletResponse.SC_UNAUTHORIZED) {
            failedAttempts.put(clientIp, failedAttempts.getOrDefault(clientIp, 0) + 1);
            logger.info("Intento fallido de autenticación desde IP {} - Intento: {}", clientIp, failedAttempts.get(clientIp));

            if (failedAttempts.get(clientIp) >= MAX_FAILED_ATTEMPTS) {
                blockedIps.put(clientIp, LocalDateTime.now());
                logger.warn("IP {} bloqueada por exceder los intentos fallidos de autenticación.", clientIp);
                sendBlockedIpToQueue(clientIp);
            }
        } else {
            failedAttempts.remove(clientIp);
        }

        return null;
    }

    private void sendBlockedIpToQueue(String clientIp) {
        String rabbitmqHost = System.getenv("RABBITMQ_HOST");
        if (rabbitmqHost == null || rabbitmqHost.isEmpty()) {
            rabbitmqHost = "rabbitmq";  // Nombre del contenedor o localhost
        }

        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(rabbitmqHost);
        factory.setPort(5672);
        factory.setUsername("guest");
        factory.setPassword("guest");
        factory.setVirtualHost("/");

        try (Connection connection = factory.newConnection();
            Channel channel = connection.createChannel()) {

            channel.queueDeclare(QUEUE_NAME, true, false, false, null);
            String message = "{\"event\": \"IP_BLOCKED\", \"ip\": \"" + clientIp + "\", \"timestamp\": \"" + LocalDateTime.now() + "\"}";
            channel.basicPublish("", QUEUE_NAME, null, message.getBytes(StandardCharsets.UTF_8));

            logger.info("Mensaje enviado a RabbitMQ: {}", message);
        } catch (Exception e) {
            logger.error("Error al conectar con RabbitMQ o enviar el mensaje", e);
        }
    }
}