package com.lance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Nacos模块Spring Boot应用启动类
 * 集成Nacos服务发现和配置管理功能
 */
@SpringBootApplication(scanBasePackages = "com.lance")
public class AgentServerApp {
    public static void main( String[] args ) {
        SpringApplication.run(AgentServerApp.class, args);
    }
}
