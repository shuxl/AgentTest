
# SkyWalking 接入方案整理

## 1. 无侵入式和侵入式接入对比

### 方案一：无侵入式（Agent 方式）⭐ **推荐**

**特点：**
- 通过 Java Agent 在 JVM 层面进行字节码增强，无需修改代码
- 通过 JVM 参数启动：`-javaagent:skywalking-agent.jar`
- 配置独立的 `agent.config` 文件

**优点：**
- ✅ 无需修改现有代码
- ✅ 对业务代码零侵入
- ✅ 无需重启服务即可开关监控
- ✅ 支持自动发现和自动埋点（Spring MVC、Feign、MyBatis、JDBC 等）
- ✅ 适合生产环境大规模使用

**缺点：**
- ❌ 需要修改启动脚本（添加 JVM 参数）
- ❌ 配置分离（agent.config vs application.yml）

**适用场景：**
- 生产环境
- 多服务监控
- 已上线项目

**启动方式：**
```bash
# 启动时添加 agent
java -javaagent:/path/to/skywalking-agent.jar \
     -DSW_AGENT_NAME=pd-chat \
     -DSW_AGENT_COLLECTOR_BACKEND_SERVICES=localhost:11800 \
     -jar agentServer.jar
```

---

### 方案二：侵入式（SDK 方式）

**特点：**
- 在项目中直接引入 SkyWalking SDK 依赖
- 通过 `pom.xml` 添加 `apm-spring-boot-starter` 等依赖
- 在业务代码中手动埋点

**优点：**
- ✅ 配置集中（在 application.yml 中统一管理）
- ✅ 可以精确控制埋点位置
- ✅ 可以自定义自定义 Trace

**缺点：**
- ❌ 需要修改 pom.xml 和代码
- ❌ 需要重启服务才能开关
- ❌ 对业务代码有侵入性
- ❌ 配置复杂，容易遗漏组件

**适用场景：**
- 开发/测试环境
- 需要精细化控制追踪的场景

**依赖配置：**
```xml
<dependency>
    <groupId>org.apache.skywalking</groupId>
    <artifactId>apm-toolkit-trace</artifactId>
    <version>9.2.0</version>
</dependency>
```

---

## 2. 针对当前项目的建议

### 项目现状分析

通过代码分析，当前项目具备以下特点：

1. **技术栈：**
   - Spring Boot 3.3.5
   - Spring Cloud Alibaba 2023.0.1.0
   - FeignClient（已有自定义拦截器）
   - MyBatis + P6Spy
   - Nacos 服务发现

2. **已有监控机制：**
   - ✅ 已有 `FeignLoggingInterceptor` 用于请求追踪
   - ✅ 已有 `P6Spy` 用于 SQL 监控
   - ✅ 已有自定义日志框架

3. **模块结构：**
   - agentServer（主服务）
   - mcp、nacos、mybatis 等功能模块

### 推荐方案：无侵入式 Agent + 配置增强

**理由：**
1. 项目已经有完善的日志追踪机制，Agent 方式可以无缝集成
2. 可以保留现有的日志拦截器，同时获得 SkyWalking 的分布式追踪能力
3. 适合多环境部署（开发/测试/生产）
4. 升级和维护成本低

---

## 3. 具体接入步骤

### 步骤一：下载 SkyWalking Agent

```bash
# 下载 SkyWalking 9.2.0（与当前 Java 17 兼容）
wget https://archive.apache.org/dist/skywalking/9.2.0/apache-skywalking-java-agent-9.2.0.tgz
tar -xzf apache-skywalking-java-agent-9.2.0.tgz
```

### 步骤二：配置 Agent（推荐集中管理）

在项目根目录创建 `skywalking` 目录存放配置：

```bash
mkdir -p skywalking/agent
# 将下载的 agent 复制到该目录
```

创建 `skywalking/agent/agent.config`：

```properties
# agent.config

# 服务名称（与 Spring application.name 保持一致）
agent.service_name=${SW_AGENT_NAME:pd-chat}

# SkyWalking OAP 服务器地址
collector.backend_service=${SW_AGENT_COLLECTOR_BACKEND_SERVICES:127.0.0.1:11800}

# 采样率（100% 采样）
plugin.toolkit.log.transmit_formatted=false

# 启用 MySQL 插件
plugin.jdbc.trace_sql_parameters=true
plugin.mysql.trace_sql_parameters=true

# 启用 Feign 插件
plugin.springcloud.openfeign.collect_http_params=true
plugin.http.http_headers_length_threshold=2048

# 启用 Spring MVC
plugin.springmvc.collect_http_params=true

# 日志相关配置
log.max_message_size=4096
correlation.element_max_number=3
```

### 步骤三：修改启动脚本

创建 `start-agent.sh`：

```bash
#!/bin/bash

# SkyWalking Agent 配置
SKYWALKING_AGENT_PATH="./skywalking/agent/skywalking-agent.jar"
SKYWALKING_CONFIG_PATH="./skywalking/agent/agent.config"

# JVM 参数
JVM_OPTS="-Xms512m -Xmx1024m"
SKYWALKING_OPTS="-javaagent:${SKYWALKING_AGENT_PATH}"

# 应用配置
APP_NAME=agentServer
APP_JAR="target/${APP_NAME}-1.0.0-SNAPSHOT.jar"

# 启动应用
echo "启动 ${APP_NAME} with SkyWalking Agent..."
java ${JVM_OPTS} ${SKYWALKING_OPTS} \
    -jar ${APP_JAR} \
    --spring.config.additional-location=classpath:/bootstrap.yml
```

### 步骤四：Docker 集成（可选）

如果使用 Docker，修改 Dockerfile：

```dockerfile
FROM openjdk:17-jre-slim

# 安装 SkyWalking Agent
COPY skywalking/agent /opt/skywalking/agent
ENV SW_AGENT_PATH=/opt/skywalking/agent

# 复制应用
COPY target/agentServer-1.0.0-SNAPSHOT.jar app.jar

# 启动命令
ENTRYPOINT ["java", "-javaagent:/opt/skywalking/agent/skywalking-agent.jar", \
            "-jar", "app.jar"]
```

---

## 4. 与现有日志系统的整合

### 与 P6Spy 的关系

- **P6Spy：** 专注 SQL 语句和参数监控
- **SkyWalking：** 提供完整的链路追踪（包含 SQL 性能）
- **建议：** 保留 P6Spy，SkyWalking 可以提供更高层的 SQL 追踪

### 与 FeignLoggingInterceptor 的关系

现有拦截器添加了 `X-Request-ID` 用于追踪，可以与 SkyWalking 的 Trace ID 整合：

```java
// 在 FeignLoggingInterceptor 中获取 SkyWalking Trace ID
import org.apache.skywalking.apm.toolkit.trace.ActiveSpan;

@Override
public void apply(RequestTemplate template) {
    String skywalkingTraceId = ActiveSpan.getTraceId();
    if (skywalkingTraceId != null) {
        template.header("X-Trace-ID", skywalkingTraceId);
        log.info("SkyWalking Trace ID: {}", skywalkingTraceId);
    }
    // ... 原有逻辑
}
```

---

## 5. 监控维度和能力

接入 SkyWalking 后将获得：

### 分布式链路追踪
- ✅ 跨服务调用追踪（FeignClient）
- ✅ 数据库操作追踪（MyBatis/JDBC）
- ✅ HTTP 请求追踪（Spring MVC）
- ✅ 异步操作追踪（线程池、消息队列）

### 性能监控
- ✅ SQL 慢查询监控
- ✅ HTTP 接口性能统计
- ✅ 异常率监控
- ✅ 吞吐量（TPS/QPS）

### 拓扑图
- ✅ 服务依赖关系可视化
- ✅ 服务间调用关系图

### 告警能力
- ✅ 服务响应时间告警
- ✅ 错误率告警
- ✅ 实例健康检查

---

## 6. 配置要点

### 环境隔离

通过不同配置文件区分环境：

```yaml
# bootstrap.yml
spring:
  profiles:
    active: nacos, mcp, mybatis

---
# bootstrap-uat.yml（UAT 环境）
# 添加 SkyWalking 配置
```

### 生产环境建议

1. **采样率控制：**
   ```properties
   # 降低采样率以减轻性能影响
   agent.sample_n_per_3_secs=10  # 每秒最多 10 条
   ```

2. **日志收集：**
   ```properties
   # 将日志发送到 SkyWalking
   plugin.toolkit.log.transmit_formatted=true
   ```

3. **告警规则：**
   在 SkyWalking OAP 配置告警规则，如响应时间、错误率等

---

## 7. 注意事项

### ⚠️ 与现有组件的兼容性

1. **P6Spy：** 可以共存，但建议只保留一个（优先 SkyWalking）
2. **自定义日志：** 保留现有日志逻辑，SK 只做链路追踪
3. **Feign 超时：** 调整 timeout 与 SkyWalking 采样频率

### ⚠️ 性能影响

- Agent 方式性能开销约 **3-5%**
- 建议生产环境降低采样率
- 监控应用内存和 CPU 使用率

### ⚠️ 版本兼容性

- Java 17 ✅
- Spring Boot 3.3.5 ✅
- SkyWalking 9.2.0+ ✅

---

## 8. 后续优化建议

### 阶段性实施

1. **Phase 1：基础接入（当前）**
   - 使用 Agent 方式接入
   - 配置基础监控
   - 验证链路追踪

2. **Phase 2：优化配置**
   - 根据实际性能调整采样率
   - 配置告警规则
   - 自定义 Trace 标签

3. **Phase 3：高级功能**
   - 与日志系统（ELK）集成
   - 自定义指标收集
   - 服务依赖分析

---

## 9. 快速验证

### 验证 Agent 是否生效

启动应用后检查日志：

```bash
# 应该看到类似输出
skywalking agent started in javaagent mode.
The checkpoint of spring bean initialization will be printed by spring bean loading, ...
```

查看 SkyWalking UI：
- 访问：http://localhost:8080
- 查看服务列表
- 验证 Trace 是否正常采集

---

## 10. 总结

**推荐方案：无侵入式 Agent 方式**

| 对比项 | Agent 方式 | SDK 方式 |
|--------|-----------|---------|
| 代码改动 | 无 | 需要 |
| 配置位置 | agent.config | application.yml |
| 性能影响 | 3-5% | 3-5% |
| 维护成本 | 低 | 中 |
| 生产适用 | ✅ | ⚠️ |
| 灵活性 | 高 | 中 |

**为什么选择 Agent 方式？**
1. 项目已有完善的日志机制，Agent 不干扰现有实现
2. 可以快速接入，无需修改业务代码
3. 便于多环境部署（dev/test/prod 只需改配置）
4. 适合 Spring Cloud 微服务架构
5. 升级 SkyWalking 只需更新 Agent，无需改代码

# SkyWalking 上下文管理深度分析

## 多线程、中间件上下文管理问题

### 问题一：traceId 在父子线程切换时会丢失吗？是否需要自定义 SystemContext？

**答案：使用 Agent 方式时，通常无需改造，但需要配置支持。**

#### SkyWalking 的上下文传播机制

SkyWalking Agent 使用 **ThreadLocal + ContextCarrier** 机制管理 Trace 上下文：

1. **ThreadLocal 存储：**
   - Trace 上下文存储在 `ThreadLocal` 中
   - 当前线程的 Trace 自动可用
   - 父子线程切换**默认会丢失**上下文（这是需要关注的点）

2. **Agent 自动处理的范围：**
   - ✅ Spring MVC Controller 入站/出站
   - ✅ FeignClient 调用
   - ✅ JDBC/MyBatis 操作
   - ✅ RocketMQ 生产者/消费者（需配置）
   - ✅ Kafka 生产者/消费者（需配置）
   - ⚠️ **Spring @Async 异步方法（需要额外配置）**
   - ⚠️ **自定义线程池（需要手动处理）**

#### 项目中会丢失的场景

根据你的项目配置：

```yaml:46:53:agentServer/src/main/resources/bootstrap-huizhi-uat.yml
  task:
    execution:
      pool:
        core-size: 500
        max-size: 500
        queue-capacity: 1000
        thread-name-prefix: MessageExecutor-
```

**问题分析：**
- 使用 Spring TaskExecutor 执行异步任务
- 500 个线程的大型线程池
- **异步任务中会丢失 Trace 上下文**

### 解决方案

#### 方案 1：启用 SkyWalking 的 Runnable/Callable 增强插件（推荐）⭐

这是最简单的方式，启用 Agent 的插件支持：

**在 `agent.config` 中添加：**

```properties
# 启用 Runnable/Callable 增强
plugin.thread_pool_runnable_plugin.enabled=true
plugin.thread_pool_callable_plugin.enabled=true

# 启用 Spring 异步增强
plugin.springmvc_annotation_plugin.enabled=true
```

**优点：**
- ✅ 自动处理 ThreadPoolExecutor、ExecutorService
- ✅ 无需修改代码
- ✅ 对 Spring TaskExecutor 有效

**局限性：**
- ⚠️ 仅支持标准的 `Runnable` 和 `Callable`
- ⚠️ 不支持 `CompletableFuture`（需要手动处理）

#### 方案 2：使用 SkyWalking Toolkit 手动处理（精准控制）

如果方案 1 不满足需求，需要手动处理上下文：

```java
import org.apache.skywalking.apm.toolkit.trace.CrossThread;
import org.apache.skywalking.apm.toolkit.trace.RunnableWrapper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class MessageHandleService {
    
    /**
     * 方式1：使用 @CrossThread 注解
     */
    @Async("taskExecutor")
    @CrossThread  // 自动传播上下文
    public void processMessageAsync(String message) {
        // 这里的 Trace 上下文会自动传播
        // 异步执行的操作会被关联到父 Trace
    }
    
    /**
     * 方式2：手动包装 Runnable
     */
    public void processWithWrapper(ExecutorService executor) {
        executor.execute(
            RunnableWrapper.of(() -> {
                // Trace 上下文会被正确传播
            })
        );
    }
}
```

#### 方案 3：自定义上下文传播（高级场景）

对于特殊场景，可以实现自定义上下文管理：

```java
package com.lance.agent.common.context;

import org.apache.skywalking.apm.toolkit.trace.TraceContext;
import org.slf4j.MDC;
import org.springframework.core.task.TaskDecorator;

/**
 * SkyWalking 上下文装饰器
 * 确保异步任务中 Trace 上下文正确传播
 */
public class SkyWalkingContextDecorator implements TaskDecorator {
    
    @Override
    public Runnable decorate(Runnable runnable) {
        // 捕获当前线程的 Trace 上下文
        String traceId = TraceContext.traceId();
        String segmentId = TraceContext.segmentId();
        String spanId = TraceContext.spanId();
        
        // 返回包装后的 Runnable，在新线程中恢复上下文
        return () -> {
            try {
                // 在新线程中设置上下文（如果 SkyWalking 支持手动设置）
                if (traceId != null && !traceId.isEmpty()) {
                    TraceContext.put("trace_id", traceId);
                }
                // 执行原任务
                runnable.run();
            } finally {
                // 清理
                TraceContext.clear();
            }
        };
    }
}
```

**在配置中注册装饰器：**

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    
    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(500);
        executor.setMaxPoolSize(500);
        executor.setQueueCapacity(1000);
        executor.setThreadNamePrefix("MessageExecutor-");
        // 关键：设置上下文装饰器
        executor.setTaskDecorator(new SkyWalkingContextDecorator());
        executor.initialize();
        return executor;
    }
}
```

---

### 问题二：在 Kafka、MQ 等消息队列中如何确保 traceId 不丢失？

#### SkyWalking 支持的中间件

Agent 方式对以下中间件有**自动支持**：

| 中间件 | 自动支持 | 配置项 |
|--------|---------|-------|
| RocketMQ | ✅ | `plugin.rocketmq-v4.enabled=true` |
| Kafka | ✅ | `plugin.kafka.enabled=true` |
| RabbitMQ | ✅ | 通过 Spring Boot 插件 |
| ActiveMQ | ✅ | `plugin.activemq.enabled=true` |

#### RocketMQ 配置（项目中已有）

```yaml:55:66:agentServer/src/main/resources/bootstrap-huizhi-uat.yml
    # aliyun:
    #   rocketmq:
    #     accessKey: ${devops.aliyun.ram.accessKey}
    #     secretKey: ${devops.aliyun.ram.secretKey}
    #     nameServer: http://MQ_INST_1706955479579371_BYwHhGyS.cn-shanghai.mq-vpc.aliyuncs.com:8080
    #     topic: PD_CHAT_USER_MESSAGE
    #     groupId: GID_PD_CHAT_SERVICE
    #     tags: '*'
    #     enable: true
    #     enableMsgConsume: true
    #     consumeThreads: 10
    #     consumeTimeout: 2
```

**Agent 配置：**

```properties
# agent.config

# 启用 RocketMQ 插件
plugin.rocketmq-v4.enabled=true
plugin.rocketmq-v4.collect_consume_params=true

# 采样消息内容（可选，注意数据安全）
plugin.rocketmq-v4.collect_message_content=true
```

#### 如何工作？

SkyWalking 的工作原理：

1. **生产者发送消息时：**
   - Agent 拦截消息发送
   - 将 Trace ID 等信息写入消息的**用户属性（User Properties）**
   - 格式：`sw-tracecontext` 或类似的 header

2. **消费者消费消息时：**
   - Agent 拦截消息消费
   - 从消息属性中提取 Trace ID
   - 创建新的 Trace（作为子 Span）或延续原有 Trace
   - 自动关联到生产者的 Trace

3. **跨服务调用链路：**
   ```
   服务A → RocketMQ → 服务B → RocketMQ → 服务C
   Trace1     ↓         Trace2     ↓      Trace3
               └─────────────────────────┘
                 完整链路追踪
   ```

#### 消息中携带的 Trace 信息

Agent 会自动在消息中添加：

```java
// 生产者代码（无需修改）
rocketMQTemplate.convertAndSend("topic", message);
// Agent 会自动添加 trace 信息到消息属性

// 消费者代码（无需修改）
@RocketMQMessageListener(...)
public class Consumer {
    @RocketMQMessageListener(...)
    public void consume(Message msg) {
        // Trace 上下文已自动恢复
        // 可以获取 Trace ID
        String traceId = TraceContext.traceId();
    }
}
```

---

## 关键配置总结

### 针对当前项目的 agent.config

```properties
# ===== 基础配置 =====
agent.service_name=${SW_AGENT_NAME:pd-chat}
collector.backend_service=${SW_AGENT_COLLECTOR_BACKEND_SERVICES:127.0.0.1:11800}

# ===== 线程池和异步支持 =====
# 启用 Runnable/Callable 增强（支持异步）
plugin.thread_pool_runnable_plugin.enabled=true
plugin.thread_pool_callable_plugin.enabled=true

# Spring 异步方法支持
plugin.springmvc_annotation_plugin.enabled=true

# ===== 消息队列支持 =====
# RocketMQ 插件
plugin.rocketmq-v4.enabled=true
plugin.rocketmq-v4.collect_consume_params=true

# 如果使用 Kafka
plugin.kafka.enabled=true
plugin.kafka.collect_consume_params=true

# ===== HTTP 和 Feign =====
plugin.springcloud.openfeign.collect_http_params=true
plugin.springmvc.collect_http_params=true

# ===== 数据库 =====
plugin.jdbc.trace_sql_parameters=true
plugin.mysql.trace_sql_parameters=true

# ===== 性能优化 =====
# 限制采样数量（生产环境建议）
agent.sample_n_per_3_secs=-1  # -1表示不限制，生产环境可设置为10-100
```

---

## 验证上下文传播

### 测试工具类

创建测试类验证上下文是否正确传播：

```java
package com.lance.agent.test;

import org.apache.skywalking.apm.toolkit.trace.TraceContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class TraceContextTestService {
    
    private static final Logger log = LoggerFactory.getLogger(TraceContextTestService.class);
    
    /**
     * 测试异步任务中的 Trace 上下文
     */
    @Async("taskExecutor")
    public void testAsyncTask(String testData) {
        String traceId = TraceContext.traceId();
        log.info("=== 异步任务中获取 Trace ID: {} ===", traceId);
        
        if (traceId == null || traceId.isEmpty()) {
            log.error("❌ Trace ID 丢失！需要检查配置");
        } else {
            log.info("✅ Trace ID 正确传播: {}", traceId);
        }
    }
}
```

在 Controller 中调用：

```java
@GetMapping("/test/trace")
public String testTrace() {
    log.info("主线程 Trace ID: {}", TraceContext.traceId());
    messageService.testAsyncTask("test");
    return "check logs";
}
```

### 检查日志

启动应用后，访问测试接口，应该看到：

```
INFO  [controller-thread] 主线程 Trace ID: [traceId:xxx]
INFO  [MessageExecutor-1] === 异步任务中获取 Trace ID: xxx ===
INFO  [MessageExecutor-1] ✅ Trace ID 正确传播: xxx
```

**如果没有 Trace ID 或 ID 不同，说明上下文丢失。**

---

## 是否需要做代码改造？

### 结论：通常不需要，但需要正确配置

| 场景 | 需要代码改造？ | 解决方案 |
|------|--------------|---------|
| Spring MVC Controller | ❌ 否 | Agent 自动处理 |
| FeignClient | ❌ 否 | Agent 自动处理 |
| MyBatis/JDBC | ❌ 否 | Agent 自动处理 |
| RocketMQ/Kafka | ❌ 否 | Agent + 插件 |
| Spring @Async | ⚠️ **可能需要** | 启用插件或手动处理 |
| 自定义线程池 | ⚠️ **可能需要** | 启用插件或手动处理 |
| CompletableFuture | ✅ **需要** | 使用 Toolkit API |

### 推荐做法

1. **优先启用 Agent 插件**（最简单）
2. **如果插件不满足需求**，使用 SkyWalking Toolkit API
3. **特殊场景**，考虑自定义装饰器（TaskDecorator）

**不需要实现自定义的 SystemContext**，SkyWalking 已经有完善的机制。

---

## 总结

### 关键技术点

1. **Agent 方式优势：**
   - 自动处理大部分场景
   - ThreadLocal + ContextCarrier 机制
   - 对常用组件有插件支持

2. **需要关注的场景：**
   - ⚠️ 自定义线程池可能丢失上下文
   - ⚠️ Spring @Async 可能丢失上下文
   - ✅ 通过配置插件或使用 API 解决

3. **消息队列支持：**
   - ✅ RocketMQ、Kafka 等主流 MQ 都有支持
   - ✅ 自动在消息中携带 Trace 信息
   - ✅ 消费者自动恢复上下文

### 针对你项目的建议

1. **启用插件支持：**
   ```properties
   plugin.thread_pool_runnable_plugin.enabled=true
   plugin.springmvc_annotation_plugin.enabled=true
   plugin.rocketmq-v4.enabled=true
   ```

2. **验证有效性：**
   - 编写测试代码验证上下文传播
   - 在 SkyWalking UI 中查看完整的 Trace

3. **监控性能影响：**
   - 大型线程池（500 线程）需要注意采样率
   - 建议生产环境设置采样限制

**总的来说，Agent 方式已经足够强大，大多数场景无需代码改造！**