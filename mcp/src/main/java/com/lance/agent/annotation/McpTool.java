package com.lance.agent.annotation;

import org.springframework.stereotype.Component;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * MCP工具服务标记注解
 * 用于标记MCP工具服务类，便于自动扫描和注册
 * 
 * @author lance
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Component
public @interface McpTool {
    /**
     * 工具服务名称
     * @return 服务名称
     */
    String value() default "";
}
