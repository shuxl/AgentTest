package com.lance.agent.config.feign;

import feign.RequestInterceptor;
import feign.RequestTemplate;
import lombok.extern.log4j.Log4j2;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.stereotype.Component;

import java.util.Date;

/**
 * Feign请求日志拦截器（合并了请求日志和响应追踪功能）
 */
@Log4j2
@Component
public class FeignLoggingInterceptor implements RequestInterceptor {

    // 使用ThreadLocal存储请求开始时间
    private static final ThreadLocal<Long> START_TIME = new ThreadLocal<>();

    @Override
    public void apply(RequestTemplate template) {
        // 记录请求开始时间
        long startTime = System.currentTimeMillis();
        START_TIME.set(startTime);

        // 添加请求ID用于追踪
        String requestId = "req_" + System.currentTimeMillis() + "_" + Thread.currentThread().getId();
        template.header("X-Request-ID", requestId);

        // 构建请求信息字符串
        StringBuilder requestInfo = new StringBuilder();
        requestInfo.append("Feign请求开始 - 请求ID: ").append(requestId)
                   .append(", URL: ").append(template.feignTarget().url()).append(" ").append(template.url());

        // 添加查询参数
        if (template.queries() != null && !template.queries().isEmpty()) {
            requestInfo.append(", 查询参数: ").append(template.queries());
        }

        // 添加请求体
        if (template.body() != null) {
            requestInfo.append(", 请求体: ").append(new String(template.body()));
        }

        // 添加请求头（简化显示）
        if (template.headers() != null && !template.headers().isEmpty()) {
            requestInfo.append(", 请求头: ").append(template.headers().size()).append("个");
        }

        requestInfo.append(", 时间: ").append(new Date(startTime));

        log.info(requestInfo.toString());
    }


    /**
     * 获取请求开始时间
     */
    public static Long getStartTime() {
        return START_TIME.get();
    }

    /**
     * 清除ThreadLocal
     */
    public static void clearStartTime() {
        START_TIME.remove();
    }
}
