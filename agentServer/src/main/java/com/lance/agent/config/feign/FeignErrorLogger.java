package com.lance.agent.config.feign;

import feign.Response;
import feign.codec.ErrorDecoder;
import lombok.extern.log4j.Log4j2;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * Feign异常日志处理器
 */
@Component
@Log4j2
public class FeignErrorLogger implements ErrorDecoder {

    @Override
    public Exception decode(String methodKey, Response response) {
        // 构建异常信息字符串
        StringBuilder errorInfo = new StringBuilder();
        errorInfo.append("Feign请求异常 - 方法: ").append(methodKey)
                .append(", 状态码: ").append(response.status());

        // 添加响应头信息（简化显示）
        if (response.headers() != null && !response.headers().isEmpty()) {
            errorInfo.append(", 响应头: ").append(response.headers().size()).append("个");
        }

        // 记录响应体
        if (response.body() != null) {
            try {
                byte[] bodyBytes = response.body().asInputStream().readAllBytes();
                String errorBody = new String(bodyBytes, StandardCharsets.UTF_8);
                errorInfo.append(", 错误响应体: ").append(errorBody);
            } catch (IOException e) {
                errorInfo.append(", 错误响应体读取失败: ").append(e.getMessage());
            }
        }

        errorInfo.append(", 时间: ").append(new Date());

        // 记录异常日志
        log.error(errorInfo.toString());

        // 根据状态码返回不同的异常
        switch (response.status()) {
            case 400:
                return new IllegalArgumentException("请求参数错误");
            case 401:
                return new SecurityException("未授权访问");
            case 403:
                return new SecurityException("禁止访问");
            case 404:
                return new RuntimeException("服务不存在");
            case 500:
                return new RuntimeException("服务内部错误");
            default:
                return new RuntimeException("服务调用失败，状态码: " + response.status());
        }
    }
}
