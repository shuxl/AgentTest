package com.lance.nacos;

import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Configuration;

/**
 * Nacos配置类
 * 用于管理Nacos相关的配置和注解
 */
@Configuration
@EnableDiscoveryClient
public class NacosConfig {
    
    // 后续可以在这里添加更多的Nacos相关配置
    // 例如：
    // - Nacos配置中心的配置
    // - 服务发现的自定义配置
    // - 健康检查配置等
    
}
