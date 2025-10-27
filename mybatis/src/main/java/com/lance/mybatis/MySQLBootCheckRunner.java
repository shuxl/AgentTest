package com.lance.mybatis;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;

import java.util.List;

/**
 * MySQL 启动检查 Runner
 * 在应用启动时检查 MyBatis Mapper 是否正确配置和可用
 */
@Order(Integer.MIN_VALUE)
public class MySQLBootCheckRunner {
    
    private static final Logger log = LoggerFactory.getLogger(MySQLBootCheckRunner.class);
    
    @Autowired(required = false)
    private List<BaseMapper<?>> mappers;
    
    @Value("${mybatis.boot.check.block:true}")
    private boolean block = true;

    @PostConstruct
    public void checkMybatisMappers() {
        if (mappers == null || mappers.isEmpty()) {
            log.warn("未找到任何 MyBatis Mapper，请检查配置");
            return;
        }
        
        try {
            log.info("开始检查 MyBatis Mapper 配置，共找到 {} 个 Mapper", mappers.size());
            mappers.forEach(item -> {
                try {
//                    item.selectList((Wrapper)(new LambdaQueryWrapper()).last("limit 1"));
                    item.selectList((Wrapper) new LambdaQueryWrapper().last("limit 1"));
                } catch (Exception e) {
                    log.warn("检查 Mapper {} 时出错: {}", item.getClass().getSimpleName(), e.getMessage());
                }
            });
            log.info("MyBatis Mapper 检查完成");
        } catch (Throwable t) {
            if (block) {
                log.error("MyBatis Mapper 启动检查失败", t);
                throw new RuntimeException("MyBatis Mapper 启动检查失败", t);
            }
            log.error("MyBatis Mapper 存在错误", t);
        }
    }
}
