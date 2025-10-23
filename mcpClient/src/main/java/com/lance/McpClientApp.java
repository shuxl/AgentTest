package com.lance;

import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.spec.McpSchema;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.List;

/**
 * Nacos模块Spring Boot应用启动类
 * 集成Nacos服务发现和配置管理功能
 */
@SpringBootApplication
public class McpClientApp {
    public static void main( String[] args ) {
        SpringApplication.run(McpClientApp.class, args);
    }

    @Bean
    public CommandLineRunner chatbot(List<McpSyncClient> mcpSyncClients) {
        return args -> {
            System.out.println("=== 应用启动完成，开始打印MCP工具信息 ===");
            for (McpSyncClient mcpSyncClient : mcpSyncClients) {
                System.out.println("MCP客户端连接成功，工具列表：");
                for (McpSchema.Tool tool : mcpSyncClient.listTools().tools()) {
                    System.out.println("----------------------------------------");
                    System.out.println("工具名称: " + tool.name());
                    System.out.println("工具描述: " + tool.description());
                    System.out.println("----------------------------------------");
                }
            }
            System.out.println("=== MCP工具信息打印完成 ===");
        };
    }
}
