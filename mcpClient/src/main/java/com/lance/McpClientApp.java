package com.lance;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

import java.util.Arrays;

/**
 * Nacos模块Spring Boot应用启动类
 * 集成Nacos服务发现和配置管理功能
 */
@SpringBootApplication
public class McpClientApp {
    public static void main( String[] args ) {
        SpringApplication.run(McpClientApp.class, args);
    }

//    @Component
//    public static class McpSyncClientBeanPrinter implements CommandLineRunner {
//
//        @Autowired
//        private ApplicationContext applicationContext;
//
//        @Override
//        public void run(String... args) throws Exception {
//            // 获取所有 McpSyncClient 类型的 bean 名称
//            String[] mcpSyncClientBeanNames = applicationContext.getBeanNamesForType(
//                org.springframework.context.annotation.Bean.class
//            );
//
//            // 查找所有包含 "McpSyncClient" 的 bean 名称
//            String[] allBeanNames = applicationContext.getBeanDefinitionNames();
//            System.out.println("=== 所有 McpSyncClient 相关的 Bean 名称 ===");
//
//            Arrays.stream(allBeanNames)
//                .filter(beanName -> beanName.toLowerCase().contains("mcpsyncclient") ||
//                        beanName.toLowerCase().contains("mcp"))
//                .forEach(beanName -> {
//                    Object bean = applicationContext.getBean(beanName);
//                    System.out.println("Bean 名称: " + beanName + " -> 类型: " + bean.getClass().getSimpleName());
//                });
//
//            // 尝试直接查找 McpSyncClient 类型的 bean
//            try {
//                String[] mcpSyncClientBeans = applicationContext.getBeanNamesForType(
//                    Class.forName("com.lance.agent.mcp.McpSyncClient")
//                );
//                System.out.println("\n=== 直接查找 McpSyncClient 类型的 Bean ===");
//                Arrays.stream(mcpSyncClientBeans)
//                    .forEach(beanName -> System.out.println("McpSyncClient Bean: " + beanName));
//            } catch (ClassNotFoundException e) {
//                System.out.println("McpSyncClient 类未找到，尝试查找其他可能的 MCP 相关类...");
//
//                // 查找所有包含 "mcp" 的 bean
//                Arrays.stream(allBeanNames)
//                    .filter(beanName -> beanName.toLowerCase().contains("mcp"))
//                    .forEach(beanName -> {
//                        Object bean = applicationContext.getBean(beanName);
//                        System.out.println("MCP 相关 Bean: " + beanName + " -> 类型: " + bean.getClass().getName());
//                    });
//            }
//        }
//    }

    //    @Autowired
//    @Qualifier("server1")
//    private McpSyncClient mcpSyncClient;
}
