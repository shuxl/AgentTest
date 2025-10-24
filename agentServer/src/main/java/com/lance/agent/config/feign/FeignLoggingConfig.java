package com.lance.agent.config.feign;

import feign.Logger;
import feign.Request;
import feign.RequestInterceptor;
import feign.codec.ErrorDecoder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 全局Feign日志配置
 */
@Configuration
public class FeignLoggingConfig {

    @Value("${spring.application.name}")
    private String applicationName;

//    /**
//     * 全局日志级别配置
//     */
//    @Bean
//    public Logger.Level feignLoggerLevel() {
//        return Logger.Level.FULL;
//    }

    /**
     * 全局请求拦截器
     */
    @Bean
    public RequestInterceptor globalRequestInterceptor() {
        return template -> {
            // 添加全局请求头，使用动态的应用名称
            template.header("X-Request-Source", applicationName);
            template.header("X-Request-Time", String.valueOf(System.currentTimeMillis()));
        };
    }

//    /**
//     * 全局超时配置
//     */
//    @Bean
//    public Request.Options globalRequestOptions() {
//        return new Request.Options(5000, 10000); // 连接超时5秒，读取超时10秒
//    }


    /**
     * 注册合并的日志拦截器（包含请求日志和响应追踪功能）
     */
    @Bean
    public RequestInterceptor feignLoggingInterceptor() {
        return new FeignLoggingInterceptor();
    }

    /**
     * 注册异常处理器
     */
    @Bean
    public ErrorDecoder feignErrorLogger() {
        return new FeignErrorLogger();
    }
}
