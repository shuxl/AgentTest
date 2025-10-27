package com.lance.mybatis;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis-Plus 自动配置类
 * 提供 MyBatis-Plus 拦截器和启动检查
 */
@Configuration
public class MyBatisPlusAutoConfiguration {

    /**
     * 配置 MyBatis-Plus 拦截器
     * 添加分页插件
     */
    @Bean
    @ConditionalOnMissingBean(MybatisPlusInterceptor.class)
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }

    /**
     * MySQL 启动检查 Runner
     * 检查 MyBatis Mapper 是否正确配置
     */
    @Bean
    @ConditionalOnProperty(
            name = "mybatis.boot.check.enable",
            havingValue = "true",
            matchIfMissing = true
    )
    public MySQLBootCheckRunner mySQLBootCheckRunner() {
        return new MySQLBootCheckRunner();
    }
}
