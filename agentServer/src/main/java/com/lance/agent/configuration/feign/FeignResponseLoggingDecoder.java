package com.lance.agent.configuration.feign;

import feign.Response;
import feign.codec.Decoder;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.ObjectFactory;
import org.springframework.boot.autoconfigure.http.HttpMessageConverters;
import org.springframework.cloud.openfeign.support.SpringDecoder;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * Feign响应日志解码器
 * 通过自定义Decoder来实现响应日志记录
 */
@Log4j2
@Component
public class FeignResponseLoggingDecoder implements Decoder {

    private final SpringDecoder delegate;

    public FeignResponseLoggingDecoder(ObjectFactory<HttpMessageConverters> messageConverters) {
        this.delegate = new SpringDecoder(messageConverters);
    }

    @Override
    public Object decode(Response response, Type type) throws IOException {
        // 先读取响应体内容用于日志记录
        byte[] responseBodyBytes = null;
        String responseBodyStr = null;

        if (response.body() != null) {
            try {
                responseBodyBytes = response.body().asInputStream().readAllBytes();
                responseBodyStr = new String(responseBodyBytes, StandardCharsets.UTF_8);
            } catch (IOException e) {
                log.warn("读取响应体失败: {}", e.getMessage());
            }
        }

        // 记录响应日志
        logResponse(response, responseBodyStr);

        // 重新创建Response对象，使用读取的响应体内容
        Response newResponse = response;
        if (responseBodyBytes != null) {
            newResponse = Response.builder()
                    .status(response.status())
                    .reason(response.reason())
                    .headers(response.headers())
                    .request(response.request())
                    .body(responseBodyBytes)
                    .build();
        }

        // 调用原始的decoder进行解码
        return delegate.decode(newResponse, type);
    }

    private void logResponse(Response response, String responseBody) {
        try {
            // 获取请求开始时间
            Long startTime = FeignLoggingInterceptor.getStartTime();
            if (startTime == null) {
                startTime = System.currentTimeMillis();
            }
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 构建响应信息字符串
            StringBuilder responseInfo = new StringBuilder();
            responseInfo.append("Feign响应结束 - URL: ").append(response.request().url())
                       .append(", 状态码: ").append(response.status())
                       .append(", 耗时: ").append(duration).append("ms");

            // 添加响应头信息（简化显示）
            if (response.headers() != null && !response.headers().isEmpty()) {
                responseInfo.append(", 响应头: ").append(response.headers().size()).append("个");
            }

            // 记录响应体
            if (responseBody != null && !responseBody.isEmpty()) {
                responseInfo.append(", 响应体: ").append(responseBody);
            }

            responseInfo.append(", 时间: ").append(new Date(endTime));

            // 根据响应状态码记录不同级别的日志
            if (response.status() >= 400) {
                log.error(responseInfo.toString());
            } else {
                log.info(responseInfo.toString());
            }

        } catch (Exception e) {
            log.warn("记录响应日志失败: {}", e.getMessage());
        } finally {
            // 清除ThreadLocal
            FeignLoggingInterceptor.clearStartTime();
        }
    }
}
