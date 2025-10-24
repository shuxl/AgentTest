# SpringFox 到 SpringDoc 迁移指南

## 概述

SpringFox 项目已经停止维护，而 SpringDoc 作为社区维护的替代方案，提供了更好的 Spring Boot 兼容性和更活跃的社区支持。本文档详细说明了从 SpringFox 迁移到 SpringDoc 的所有变化和步骤。

## 1. 依赖管理变化

### 1.1 移除 SpringFox 依赖

**移除的依赖：**
```xml
<!-- SpringFox 相关依赖 -->
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger2</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger-ui</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-boot-starter</artifactId>
    <version>3.0.0</version>
</dependency>
```

### 1.2 添加 SpringDoc 依赖

**Spring Web MVC 项目：**
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.2.0</version>
</dependency>
```

**Spring WebFlux 项目：**
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webflux-ui</artifactId>
    <version>2.2.0</version>
</dependency>
```

## 2. 注解映射对照表

| SpringFox 注解 | SpringDoc 注解 | 说明 | 参数变化 |
|----------------|----------------|------|----------|
| `@Api` | `@Tag` | 标记控制器类 | `value` → `name`, `description` |
| `@ApiOperation` | `@Operation` | 描述接口方法 | `value` → `summary`, `notes` → `description` |
| `@ApiParam` | `@Parameter` | 描述方法参数 | `value` → `description` |
| `@ApiModel` | `@Schema` | 描述数据模型 | `value` → `title`, `description` |
| `@ApiModelProperty` | `@Schema` | 描述模型属性 | `value` → `description` |
| `@ApiImplicitParam` | `@Parameter` | 描述隐式参数 | 参数结构有变化 |
| `@ApiImplicitParams` | `@Parameters` | 描述多个隐式参数 | 包装注解 |
| `@ApiResponse` | `@ApiResponse` | 描述响应信息 | 参数名称有变化 |
| `@ApiResponses` | `@ApiResponses` | 描述多个响应信息 | 保持不变 |
| `@ApiIgnore` | `@Hidden` 或 `@Operation(hidden=true)` | 隐藏接口或参数 | 使用方式有变化 |

## 3. 详细注解迁移示例

### 3.1 控制器类注解

**SpringFox 写法：**
```java
@Api(value = "用户管理", tags = "User Management")
@RestController
@RequestMapping("/users")
public class UserController {
    // ...
}
```

**SpringDoc 写法：**
```java
@Tag(name = "User Management", description = "用户管理")
@RestController
@RequestMapping("/users")
public class UserController {
    // ...
}
```

### 3.2 方法注解

**SpringFox 写法：**
```java
@ApiOperation(value = "获取用户信息", notes = "根据用户ID获取详细信息")
@ApiResponses({
    @ApiResponse(code = 200, message = "成功"),
    @ApiResponse(code = 404, message = "用户不存在")
})
@GetMapping("/{id}")
public ResponseEntity<User> getUser(@ApiParam(value = "用户ID", required = true) @PathVariable Long id) {
    // ...
}
```

**SpringDoc 写法：**
```java
@Operation(summary = "获取用户信息", description = "根据用户ID获取详细信息")
@ApiResponses({
    @ApiResponse(responseCode = "200", description = "成功"),
    @ApiResponse(responseCode = "404", description = "用户不存在")
})
@GetMapping("/{id}")
public ResponseEntity<User> getUser(@Parameter(description = "用户ID", required = true) @PathVariable Long id) {
    // ...
}
```

### 3.3 模型类注解

**SpringFox 写法：**
```java
@ApiModel(description = "用户信息")
public class User {
    @ApiModelProperty(value = "用户ID", example = "1")
    private Long id;
    
    @ApiModelProperty(value = "用户名", example = "john_doe", required = true)
    private String username;
    
    @ApiModelProperty(value = "邮箱", example = "john@example.com")
    private String email;
}
```

**SpringDoc 写法：**
```java
@Schema(description = "用户信息")
public class User {
    @Schema(description = "用户ID", example = "1")
    private Long id;
    
    @Schema(description = "用户名", example = "john_doe", required = true)
    private String username;
    
    @Schema(description = "邮箱", example = "john@example.com")
    private String email;
}
```

### 3.4 隐藏接口

**SpringFox 写法：**
```java
@ApiIgnore
@PostMapping("/internal")
public void internalMethod() {
    // ...
}
```

**SpringDoc 写法：**
```java
@Hidden
@PostMapping("/internal")
public void internalMethod() {
    // ...
}

// 或者使用 @Operation
@Operation(hidden = true)
@PostMapping("/internal")
public void internalMethod() {
    // ...
}
```

## 4. 配置变化

### 4.1 SpringFox 配置（需要移除）

**SpringFox 配置类：**
```java
@Configuration
@EnableSwagger2
public class SwaggerConfig {
    @Bean
    public Docket api() {
        return new Docket(DocumentationType.SWAGGER_2)
                .select()
                .apis(RequestHandlerSelectors.basePackage("com.example.controller"))
                .paths(PathSelectors.any())
                .build()
                .apiInfo(apiInfo());
    }
    
    private ApiInfo apiInfo() {
        return new ApiInfoBuilder()
                .title("API 文档")
                .description("系统 API 接口文档")
                .version("1.0")
                .build();
    }
}
```

### 4.2 SpringDoc 配置

**application.yml 配置：**
```yaml
springdoc:
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
    operations-sorter: method
    tags-sorter: alpha
  api-docs:
    path: /v3/api-docs
    enabled: true
  packages-to-scan: com.example.controller
  show-actuator: false
```

**Java 配置（可选）：**
```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("API 文档")
                        .description("系统 API 接口文档")
                        .version("1.0"))
                .addServersItem(new Server().url("http://localhost:8080"));
    }
}
```

## 5. 访问路径变化

| 功能 | SpringFox | SpringDoc |
|------|-----------|-----------|
| Swagger UI | `/swagger-ui.html` | `/swagger-ui/index.html` |
| API 文档 (JSON) | `/v2/api-docs` | `/v3/api-docs` |
| API 文档 (YAML) | `/v2/api-docs.yaml` | `/v3/api-docs.yaml` |

## 6. 迁移步骤

### 6.1 准备工作
1. 备份现有代码
2. 确保项目使用 Spring Boot 2.6+ 版本
3. 检查现有 SpringFox 版本

### 6.2 执行迁移
1. **移除 SpringFox 依赖**
2. **添加 SpringDoc 依赖**
3. **替换注解**：按照对照表逐一替换
4. **删除 SpringFox 配置类**
5. **添加 SpringDoc 配置**（可选）
6. **测试验证**

### 6.3 验证迁移
1. 启动应用
2. 访问 `/swagger-ui/index.html` 检查 UI
3. 访问 `/v3/api-docs` 检查 JSON 文档
4. 测试 API 接口功能

## 7. 常见问题

### 7.1 依赖冲突
**问题：** SpringDoc 与 SpringFox 依赖冲突
**解决：** 确保完全移除 SpringFox 依赖

### 7.2 注解不生效
**问题：** 替换注解后文档不显示
**解决：** 检查包扫描配置，确保控制器在扫描范围内

### 7.3 版本兼容性
**问题：** SpringDoc 版本与 Spring Boot 版本不兼容
**解决：** 参考官方兼容性矩阵选择合适版本

## 8. 最佳实践

1. **渐进式迁移**：建议先在测试环境验证
2. **版本选择**：选择稳定版本，避免使用 SNAPSHOT 版本
3. **配置优化**：根据项目需求调整 SpringDoc 配置
4. **文档完善**：利用 SpringDoc 的丰富功能完善 API 文档

## 9. 总结

SpringDoc 相比 SpringFox 具有以下优势：
- ✅ 更好的 Spring Boot 兼容性
- ✅ 活跃的社区维护
- ✅ 支持 OpenAPI 3.0 规范
- ✅ 更简洁的配置方式
- ✅ 更丰富的自定义选项

迁移到 SpringDoc 虽然需要修改注解和配置，但能获得更好的长期维护支持和技术生态。
