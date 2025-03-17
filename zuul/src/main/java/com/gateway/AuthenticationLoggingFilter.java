package com.gateway;

import com.netflix.zuul.ZuulFilter;
import com.netflix.zuul.context.RequestContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
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
            }
        } else {
            failedAttempts.remove(clientIp);
        }

        return null;
    }

    private void handleBlockedIp(RequestContext ctx, String clientIp) {
        if (isIpBlocked(clientIp)) {
            if (isBlockStillActive(clientIp)) {
                blockResponse(ctx, clientIp);
            } else {
                unblockIp(clientIp);
            }
        }
    }
}