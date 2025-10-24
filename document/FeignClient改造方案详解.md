# FeignClient改造方案详解

## 目录
1. [项目现状分析](#项目现状分析)
2. [FeignClient Configuration特殊处理](#feignclient-configuration特殊处理)
3. [Fallback和FallbackFactory机制](#fallback和fallbackfactory机制)
4. [统一日志打印方案](#统一日志打印方案)
5. [完整改造示例](#完整改造示例)
6. [最佳实践建议](#最佳实践建议)

## 项目现状分析

### 当前项目FeignClient使用情况

根据项目代码分析，当前项目中有以下FeignClient：

1. **DoctorScheduleApi** - 医生排班服务API
```java
@FeignClient(
    value = "doctor-service",
    path = "/sdk/schedule"
)
public interface DoctorScheduleApi {
    @GetMapping({"/detail/v2"})
    ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(@RequestParam("doctorId") Long var1);
}
```

2. **DoctorWorkbenchServiceApi** - 血压服务医生工作台API
```java
@FeignClient(
    value = "blood-pressure-service",
    path = "/doctorWorkbench"
)
public interface DoctorWorkbenchServiceApi {
    @GetMapping({"getBindDoctorId"})
    Object getBindDoctorId(@RequestParam("patientId") Long var1);
}
```

### 当前配置
- 使用`@EnableFeignClients`扫描`com.lance.agent.feign.**`包
- 基础配置较为简单，缺乏容错和监控机制

## FeignClient Configuration特殊处理

### 1. 自定义配置类

可以为特定的FeignClient创建专门的配置类，实现特殊处理需求：

```java
/**
 * 医生服务Feign配置
 * 注意：不要使用@Configuration注解，避免被全局扫描
 */
public class DoctorServiceFeignConfig {
    
    /**
     * 自定义解码器
     */
    @Bean
    public Decoder doctorServiceDecoder() {
        return new OptionalDecoder(new ResponseEntityDecoder(new SpringDecoder(messageConverters()))) {
            @Override
            public Object decode(Response response, Type type) throws IOException, FeignException {
                // 特殊处理医生服务的响应
                if (response.status() == 404) {
                    return new ApiResult<>(404, "医生信息不存在", null);
                }
                return super.decode(response, type);
            }
        };
    }
    
    /**
     * 自定义编码器
     */
    @Bean
    public Encoder doctorServiceEncoder() {
        return new SpringEncoder(messageConverters());
    }
    
    /**
     * 自定义错误解码器
     */
    @Bean
    public ErrorDecoder doctorServiceErrorDecoder() {
        return new ErrorDecoder() {
            @Override
            public Exception decode(String methodKey, Response response) {
                switch (response.status()) {
                    case 400:
                        return new IllegalArgumentException("请求参数错误");
                    case 401:
                        return new SecurityException("未授权访问");
                    case 500:
                        return new RuntimeException("医生服务内部错误");
                    default:
                        return new RuntimeException("医生服务调用失败");
                }
            }
        };
    }
    
    /**
     * 设置日志级别
     */
    @Bean
    public Logger.Level doctorServiceLoggerLevel() {
        return Logger.Level.FULL;
    }
    
    /**
     * 自定义重试器
     */
    @Bean
    public Retryer doctorServiceRetryer() {
        return new Retryer.Default(1000, 2000, 3);
    }
    
    /**
     * 消息转换器
     */
    @Bean
    public List<HttpMessageConverter<?>> messageConverters() {
        List<HttpMessageConverter<?>> converters = new ArrayList<>();
        converters.add(new MappingJackson2HttpMessageConverter());
        converters.add(new StringHttpMessageConverter());
        return converters;
    }
}
```

### 2. 使用自定义配置

```java
@FeignClient(
    value = "doctor-service",
    path = "/sdk/schedule",
    configuration = DoctorServiceFeignConfig.class  // 使用自定义配置
)
public interface DoctorScheduleApi {
    @GetMapping({"/detail/v2"})
    ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(@RequestParam("doctorId") Long var1);
}
```

### 3. 全局Feign配置

```java
@Configuration
public class GlobalFeignConfig {
    
    /**
     * 全局请求拦截器
     */
    @Bean
    public RequestInterceptor globalRequestInterceptor() {
        return template -> {
            // 添加全局请求头
            template.header("X-Request-Source", "agent-server");
            template.header("X-Request-Time", String.valueOf(System.currentTimeMillis()));
        };
    }
    
    /**
     * 全局日志配置
     */
    @Bean
    public Logger.Level globalLoggerLevel() {
        return Logger.Level.BASIC;
    }
    
    /**
     * 全局超时配置
     */
    @Bean
    public Request.Options globalRequestOptions() {
        return new Request.Options(5000, 10000); // 连接超时5秒，读取超时10秒
    }
}
```

## Fallback和FallbackFactory机制

### 1. Fallback机制

Fallback是FeignClient的降级机制，当远程调用失败时执行预定义的回退逻辑。

#### 1.1 创建Fallback类

```java
/**
 * 医生排班服务降级处理
 */
@Component
public class DoctorScheduleApiFallback implements DoctorScheduleApi {
    
    private static final Logger log = LoggerFactory.getLogger(DoctorScheduleApiFallback.class);
    
    @Override
    public ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(Long doctorId) {
        log.warn("医生排班服务调用失败，执行降级逻辑，doctorId: {}", doctorId);
        
        // 返回默认的排班信息
        DoctorScheduleSettingV2 defaultSchedule = new DoctorScheduleSettingV2();
        defaultSchedule.setDoctorId(doctorId);
        defaultSchedule.setStatus("服务暂不可用");
        
        return ApiResult.success(defaultSchedule);
    }
}
```

#### 1.2 使用Fallback

```java
@FeignClient(
    value = "doctor-service",
    path = "/sdk/schedule",
    configuration = DoctorServiceFeignConfig.class,
    fallback = DoctorScheduleApiFallback.class  // 指定降级处理类
)
public interface DoctorScheduleApi {
    @GetMapping({"/detail/v2"})
    ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(@RequestParam("doctorId") Long var1);
}
```

### 2. FallbackFactory机制

FallbackFactory提供更细粒度的异常处理，可以获取导致失败的异常信息。

#### 2.1 创建FallbackFactory

```java
/**
 * 医生工作台服务降级工厂
 */
@Component
public class DoctorWorkbenchServiceApiFallbackFactory implements FallbackFactory<DoctorWorkbenchServiceApi> {
    
    private static final Logger log = LoggerFactory.getLogger(DoctorWorkbenchServiceApiFallbackFactory.class);
    
    @Override
    public DoctorWorkbenchServiceApi create(Throwable cause) {
        return new DoctorWorkbenchServiceApi() {
            @Override
            public Object getBindDoctorId(Long patientId) {
                // 构建异常信息字符串
                StringBuilder fallbackInfo = new StringBuilder();
                fallbackInfo.append("医生工作台服务降级 - patientId: ").append(patientId)
                          .append(", 异常类型: ").append(cause.getClass().getSimpleName())
                          .append(", 异常信息: ").append(cause.getMessage())
                          .append(", 时间: ").append(new Date());
                
                // 根据异常类型进行不同的处理
                if (cause instanceof ConnectException) {
                    fallbackInfo.append(", 处理方式: 返回默认医生ID");
                    log.warn(fallbackInfo.toString());
                    return 0L; // 返回默认医生ID
                } else if (cause instanceof SocketTimeoutException) {
                    fallbackInfo.append(", 处理方式: 返回空结果");
                    log.warn(fallbackInfo.toString());
                    return null;
                } else {
                    fallbackInfo.append(", 处理方式: 返回默认值");
                    log.warn(fallbackInfo.toString());
                    return new HashMap<String, Object>() {{
                        put("error", "服务暂不可用");
                        put("message", cause.getMessage());
                    }};
                }
            }
        };
    }
}
```

#### 2.2 使用FallbackFactory

```java
@FeignClient(
    value = "blood-pressure-service",
    path = "/doctorWorkbench",
    fallbackFactory = DoctorWorkbenchServiceApiFallbackFactory.class  // 使用降级工厂
)
public interface DoctorWorkbenchServiceApi {
    @GetMapping({"getBindDoctorId"})
    Object getBindDoctorId(@RequestParam("patientId") Long var1);
}
```

### 3. Fallback vs FallbackFactory选择

| 特性 | Fallback | FallbackFactory |
|------|----------|-----------------|
| 异常信息获取 | ❌ 无法获取 | ✅ 可以获取详细异常信息 |
| 实现复杂度 | 简单 | 稍复杂 |
| 适用场景 | 简单的降级逻辑 | 需要根据异常类型做不同处理 |
| 推荐使用 | 基础降级 | 生产环境推荐 |

## 统一日志打印方案

> **单行日志优化说明**：本方案将所有请求、响应、异常信息尽可能放在一行中，具有以下优势：
> - **提高可读性**：单行日志便于日志分析和问题排查
> - **提升性能**：减少日志I/O操作次数，降低系统开销
> - **便于监控**：单行格式便于日志收集和分析工具处理
> - **节省存储**：减少日志文件大小，节省存储空间

### 1. 自定义请求拦截器

```java
/**
 * Feign请求日志拦截器
 */
@Component
public class FeignLoggingInterceptor implements RequestInterceptor {
    
    private static final Logger log = LoggerFactory.getLogger(FeignLoggingInterceptor.class);
    
    @Override
    public void apply(RequestTemplate template) {
        // 记录请求开始时间
        long startTime = System.currentTimeMillis();
        template.requestVariables().put("startTime", String.valueOf(startTime));
        
        // 构建请求信息字符串
        StringBuilder requestInfo = new StringBuilder();
        requestInfo.append("Feign请求开始 - 服务: ").append(template.feignTarget().name())
                  .append(", URL: ").append(template.method()).append(" ").append(template.url());
        
        // 添加查询参数
        if (template.queries() != null && !template.queries().isEmpty()) {
            requestInfo.append(", 查询参数: ").append(template.queries());
        }
        
        // 添加请求体
        if (template.body() != null) {
            requestInfo.append(", 请求体: ").append(new String(template.body()));
        }
        
        // 添加请求头（简化显示）
        if (template.headers() != null && !template.headers().isEmpty()) {
            requestInfo.append(", 请求头: ").append(template.headers().size()).append("个");
        }
        
        requestInfo.append(", 时间: ").append(new Date(startTime));
        
        log.info(requestInfo.toString());
    }
}
```

### 2. 自定义响应拦截器

```java
/**
 * Feign响应日志拦截器
 */
@Component
public class FeignResponseInterceptor implements ResponseInterceptor {
    
    private static final Logger log = LoggerFactory.getLogger(FeignResponseInterceptor.class);
    
    @Override
    public void apply(Response response) {
        // 获取请求开始时间
        String startTimeStr = response.request().requestVariables().get("startTime");
        long startTime = startTimeStr != null ? Long.parseLong(startTimeStr) : System.currentTimeMillis();
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        // 构建响应信息字符串
        StringBuilder responseInfo = new StringBuilder();
        responseInfo.append("Feign响应结束 - 服务: ").append(response.request().feignTarget().name())
                   .append(", 状态码: ").append(response.status())
                   .append(", 耗时: ").append(duration).append("ms");
        
        // 添加响应头信息（简化显示）
        if (response.headers() != null && !response.headers().isEmpty()) {
            responseInfo.append(", 响应头: ").append(response.headers().size()).append("个");
        }
        
        // 记录响应体（注意：响应体只能读取一次）
        if (response.body() != null) {
            try {
                byte[] bodyBytes = response.body().asInputStream().readAllBytes();
                String responseBody = new String(bodyBytes, StandardCharsets.UTF_8);
                responseInfo.append(", 响应体: ").append(responseBody);
                
                // 重新创建响应对象，因为body已经被读取
                response = Response.builder()
                    .status(response.status())
                    .reason(response.reason())
                    .headers(response.headers())
                    .body(bodyBytes)
                    .request(response.request())
                    .build();
            } catch (IOException e) {
                responseInfo.append(", 响应体读取失败: ").append(e.getMessage());
            }
        }
        
        responseInfo.append(", 时间: ").append(new Date(endTime));
        
        // 根据响应状态码记录不同级别的日志
        if (response.status() >= 400) {
            log.error(responseInfo.toString());
        } else {
            log.info(responseInfo.toString());
        }
    }
}
```

### 3. 异常日志处理

```java
/**
 * Feign异常日志处理器
 */
@Component
public class FeignErrorLogger implements ErrorDecoder {
    
    private static final Logger log = LoggerFactory.getLogger(FeignErrorLogger.class);
    
    @Override
    public Exception decode(String methodKey, Response response) {
        // 构建异常信息字符串
        StringBuilder errorInfo = new StringBuilder();
        errorInfo.append("Feign请求异常 - 方法: ").append(methodKey)
                .append(", 状态码: ").append(response.status());
        
        // 添加响应头信息（简化显示）
        if (response.headers() != null && !response.headers().isEmpty()) {
            errorInfo.append(", 响应头: ").append(response.headers().size()).append("个");
        }
        
        // 记录响应体
        if (response.body() != null) {
            try {
                byte[] bodyBytes = response.body().asInputStream().readAllBytes();
                String errorBody = new String(bodyBytes, StandardCharsets.UTF_8);
                errorInfo.append(", 错误响应体: ").append(errorBody);
            } catch (IOException e) {
                errorInfo.append(", 错误响应体读取失败: ").append(e.getMessage());
            }
        }
        
        errorInfo.append(", 时间: ").append(new Date());
        
        // 记录异常日志
        log.error(errorInfo.toString());
        
        // 根据状态码返回不同的异常
        switch (response.status()) {
            case 400:
                return new IllegalArgumentException("请求参数错误");
            case 401:
                return new SecurityException("未授权访问");
            case 403:
                return new SecurityException("禁止访问");
            case 404:
                return new RuntimeException("服务不存在");
            case 500:
                return new RuntimeException("服务内部错误");
            default:
                return new RuntimeException("服务调用失败，状态码: " + response.status());
        }
    }
}
```

### 4. 全局日志配置

```java
/**
 * 全局Feign日志配置
 */
@Configuration
public class FeignLoggingConfig {
    
    /**
     * 全局日志级别配置
     */
    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }
    
    /**
     * 注册日志拦截器
     */
    @Bean
    public RequestInterceptor feignLoggingInterceptor() {
        return new FeignLoggingInterceptor();
    }
    
    /**
     * 注册响应拦截器
     */
    @Bean
    public ResponseInterceptor feignResponseInterceptor() {
        return new FeignResponseInterceptor();
    }
    
    /**
     * 注册异常处理器
     */
    @Bean
    public ErrorDecoder feignErrorLogger() {
        return new FeignErrorLogger();
    }
}
```

### 5. 配置文件设置

在`application.yml`中添加Feign日志配置：

```yaml
# Feign配置
feign:
  client:
    config:
      default:
        loggerLevel: FULL  # 日志级别：NONE, BASIC, HEADERS, FULL
        connectTimeout: 5000  # 连接超时时间（毫秒）
        readTimeout: 10000    # 读取超时时间（毫秒）
        retryer: com.lance.agent.config.CustomRetryer  # 自定义重试器
  compression:
    request:
      enabled: true  # 启用请求压缩
    response:
      enabled: true  # 启用响应压缩

# 日志配置
logging:
  level:
    com.lance.agent.feign: DEBUG  # Feign包下的日志级别
    feign: DEBUG                  # Feign框架日志级别
```

## 完整改造示例

### 1. 改造后的DoctorScheduleApi

```java
@FeignClient(
    value = "doctor-service",
    path = "/sdk/schedule",
    configuration = DoctorServiceFeignConfig.class,
    fallbackFactory = DoctorScheduleApiFallbackFactory.class
)
public interface DoctorScheduleApi {
    
    /**
     * 获取排班明细V2
     * @param doctorId 医生ID
     * @return 排班信息
     */
    @GetMapping({"/detail/v2"})
    ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(@RequestParam("doctorId") Long doctorId);
}
```

### 2. 对应的FallbackFactory

```java
@Component
public class DoctorScheduleApiFallbackFactory implements FallbackFactory<DoctorScheduleApi> {
    
    private static final Logger log = LoggerFactory.getLogger(DoctorScheduleApiFallbackFactory.class);
    
    @Override
    public DoctorScheduleApi create(Throwable cause) {
        return doctorId -> {
            // 构建异常信息字符串
            StringBuilder fallbackInfo = new StringBuilder();
            fallbackInfo.append("医生排班服务降级 - doctorId: ").append(doctorId)
                      .append(", 异常类型: ").append(cause.getClass().getSimpleName())
                      .append(", 异常信息: ").append(cause.getMessage())
                      .append(", 时间: ").append(new Date());
            
            // 根据异常类型返回不同的降级结果
            if (cause instanceof ConnectException) {
                fallbackInfo.append(", 处理方式: 网络连接失败");
                log.error(fallbackInfo.toString());
                return ApiResult.error("网络连接失败，请稍后重试");
            } else if (cause instanceof SocketTimeoutException) {
                fallbackInfo.append(", 处理方式: 请求超时");
                log.error(fallbackInfo.toString());
                return ApiResult.error("请求超时，请稍后重试");
            } else {
                fallbackInfo.append(", 处理方式: 服务暂不可用");
                log.error(fallbackInfo.toString());
                return ApiResult.error("服务暂不可用，请稍后重试");
            }
        };
    }
}
```

### 3. 服务层使用示例

```java
@Service
public class DoctorScheduleService {
    
    @Autowired
    private DoctorScheduleApi doctorScheduleApi;
    
    /**
     * 获取医生排班信息
     */
    public ApiResult<DoctorScheduleSettingV2> getDoctorSchedule(Long doctorId) {
        try {
            log.info("开始获取医生排班信息 - doctorId: {}, 时间: {}", doctorId, new Date());
            ApiResult<DoctorScheduleSettingV2> result = doctorScheduleApi.getScheduleDetailV2(doctorId);
            log.info("获取医生排班信息成功 - doctorId: {}, 时间: {}", doctorId, new Date());
            return result;
        } catch (Exception e) {
            log.error("获取医生排班信息异常 - doctorId: {}, 异常: {}, 时间: {}", 
                     doctorId, e.getMessage(), new Date(), e);
            return ApiResult.error("获取排班信息失败");
        }
    }
}
```

## 最佳实践建议

### 1. 配置管理
- **分离配置**：为不同的服务创建独立的配置类
- **避免全局扫描**：自定义配置类不要使用`@Configuration`注解
- **环境区分**：不同环境使用不同的超时和重试配置

### 2. 异常处理
- **优先使用FallbackFactory**：可以获取详细的异常信息
- **分类处理异常**：根据异常类型提供不同的降级策略
- **记录异常日志**：便于问题排查和监控

### 3. 日志管理
- **统一日志格式**：所有FeignClient使用相同的日志格式
- **单行日志优化**：将请求、响应、异常信息尽可能放在一行，提高日志可读性和性能
- **性能考虑**：生产环境可以适当降低日志级别
- **敏感信息**：避免在日志中记录敏感信息

### 4. 监控和告警
- **响应时间监控**：记录每个FeignClient的响应时间
- **成功率监控**：监控服务调用的成功率
- **异常告警**：对频繁的异常进行告警

### 5. 性能优化
- **连接池配置**：合理配置HTTP连接池参数
- **压缩配置**：启用请求和响应压缩
- **缓存策略**：对不经常变化的数据进行缓存

### 6. 安全考虑
- **认证信息**：在请求头中添加认证信息
- **请求签名**：对重要请求进行签名验证
- **IP白名单**：限制服务调用的来源IP

## 总结

通过以上改造方案，可以实现：

1. **特殊处理**：通过Configuration为不同服务提供定制化配置
2. **容错机制**：通过Fallback和FallbackFactory提供降级保护
3. **统一监控**：通过拦截器实现统一的日志记录和监控
4. **性能优化**：通过合理的配置提升服务调用性能
5. **运维友好**：通过详细的日志和监控信息便于运维管理

建议按照项目实际情况，逐步实施这些改造方案，优先实现容错机制和统一日志，然后根据需要进行其他优化。
