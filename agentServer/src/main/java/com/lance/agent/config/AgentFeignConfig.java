package com.lance.agent.config;

import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Configuration;

/**
 * Feign配置类
 */
@Configuration
@EnableFeignClients(basePackages = {
        "com.lance.agent.feign.**"
})
public class AgentFeignConfig {
}
