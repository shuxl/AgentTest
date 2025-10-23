package com.lance.agent.config;

import com.lance.agent.annotation.McpTool;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.function.FunctionToolCallback;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * MCP工具配置类
 * 负责扫描和注册所有带有@McpTool注解的服务
 * 
 * @author lance
 */
@Configuration
public class McpToolConfiguration {
    
    /**
     * 创建MCP工具回调提供者
     * 自动扫描所有带有@McpTool注解的服务并注册其@Tool方法
     * 
     * @param applicationContext Spring应用上下文
     * @return ToolCallbackProvider实例
     */
    @Bean
    public ToolCallbackProvider mcpTools(ApplicationContext applicationContext) {
        // 获取所有带有@McpTool注解的Bean
        Map<String, Object> mcpToolBeans = applicationContext.getBeansWithAnnotation(McpTool.class);
        
        // 将所有的MCP工具Bean转换为List
        List<Object> toolObjects = new ArrayList<>(mcpToolBeans.values());
        
        // 构建ToolCallbackProvider，注册所有MCP工具中的@Tool方法
        return MethodToolCallbackProvider.builder()
                .toolObjects(toolObjects.toArray())
                .build();
//        return MethodToolCallbackProvider.builder().toolObjects(weatherService).build();

    }

    @Bean
    public ToolCallbackProvider myTools(McpToolConfiguration mcpConfig, ApplicationContext applicationContext) {
        return mcpConfig.mcpTools(applicationContext);
    }

    public record TextInput(String input) {
    }

    @Bean
    public ToolCallback toUpperCase() {
        return FunctionToolCallback.builder("toUpperCase", (TextInput input) -> input.input().toUpperCase())
                .inputType(TextInput.class)
                .description("Put the text to upper case")
                .build();
    }
}
