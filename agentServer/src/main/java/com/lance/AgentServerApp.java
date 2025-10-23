package com.lance;

import com.lance.agent.config.McpToolConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

/**
 * Nacos模块Spring Boot应用启动类
 * 集成Nacos服务发现和配置管理功能
 */
@SpringBootApplication(scanBasePackages = "com.lance")
@Import(McpToolConfiguration.class)
public class AgentServerApp {
    public static void main( String[] args ) {
        SpringApplication.run(AgentServerApp.class, args);
    }
}
