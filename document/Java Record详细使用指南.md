# Java Record 详细使用指南

## 概述

Java Record 是 Java 14 引入的预览特性，在 Java 16 中正式发布。它是一种简洁的数据载体类，专门用于表示不可变的数据聚合。Record 自动生成构造函数、访问器方法、equals()、hashCode() 和 toString() 方法。

## 1. Record 基本语法

### 1.1 基本定义

```java
// 最简单的 Record
public record Point(int x, int y) {}

// 使用示例
Point p = new Point(10, 20);
System.out.println(p.x()); // 10
System.out.println(p.y()); // 20
System.out.println(p);     // Point[x=10, y=20]
```

### 1.2 带注解的 Record

```java
public record User(
    @Schema(description = "用户ID")
    Long id,
    
    @Schema(description = "用户名")
    String name,
    
    @JsonProperty("email_address")
    String email
) {}
```

### 1.3 实现接口的 Record

```java
public record Product(
    String name,
    BigDecimal price
) implements Serializable, Comparable<Product> {
    
    @Override
    public int compareTo(Product other) {
        return this.price.compareTo(other.price);
    }
}
```

## 2. Record 的高级特性

### 2.1 紧凑构造函数（Compact Constructor）

```java
public record Person(String name, int age) {
    // 紧凑构造函数 - 用于验证和规范化
    public Person {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("姓名不能为空");
        }
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("年龄必须在0-150之间");
        }
        // 规范化数据
        name = name.trim();
    }
}

// 使用示例
Person person = new Person("  张三  ", 25);
System.out.println(person.name()); // "张三" (已去除空格)
```

### 2.2 自定义方法

```java
public record Rectangle(double width, double height) {
    
    // 计算面积
    public double area() {
        return width * height;
    }
    
    // 计算周长
    public double perimeter() {
        return 2 * (width + height);
    }
    
    // 判断是否为正方形
    public boolean isSquare() {
        return width == height;
    }
    
    // 静态工厂方法
    public static Rectangle square(double side) {
        return new Rectangle(side, side);
    }
}

// 使用示例
Rectangle rect = new Rectangle(5.0, 3.0);
System.out.println("面积: " + rect.area());        // 15.0
System.out.println("周长: " + rect.perimeter());   // 16.0
System.out.println("是正方形: " + rect.isSquare()); // false

Rectangle square = Rectangle.square(4.0);
System.out.println("是正方形: " + square.isSquare()); // true
```

### 2.3 静态字段和方法

```java
public record Money(BigDecimal amount, String currency) {
    
    // 静态常量
    public static final String USD = "USD";
    public static final String EUR = "EUR";
    public static final String CNY = "CNY";
    
    // 静态工厂方法
    public static Money usd(BigDecimal amount) {
        return new Money(amount, USD);
    }
    
    public static Money eur(BigDecimal amount) {
        return new Money(amount, EUR);
    }
    
    public static Money cny(BigDecimal amount) {
        return new Money(amount, CNY);
    }
    
    // 实例方法
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("货币类型不匹配");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}

// 使用示例
Money usd100 = Money.usd(new BigDecimal("100.00"));
Money usd50 = Money.usd(new BigDecimal("50.00"));
Money total = usd100.add(usd50);
System.out.println(total); // Money[amount=150.00, currency=USD]
```

## 3. Record 适用场景

### 3.1 数据传输对象（DTO）

```java
// API 响应对象
public record ApiResponse<T>(
    boolean success,
    String message,
    T data,
    long timestamp
) {
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, "操作成功", data, System.currentTimeMillis());
    }
    
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(false, message, null, System.currentTimeMillis());
    }
}

// 使用示例
ApiResponse<User> response = ApiResponse.success(new User(1L, "张三", "zhangsan@example.com"));
```

### 3.2 配置对象

```java
public record DatabaseConfig(
    String host,
    int port,
    String database,
    String username,
    String password,
    int maxConnections
) {
    public DatabaseConfig {
        if (port <= 0 || port > 65535) {
            throw new IllegalArgumentException("端口号必须在1-65535之间");
        }
        if (maxConnections <= 0) {
            throw new IllegalArgumentException("最大连接数必须大于0");
        }
    }
    
    public String getConnectionUrl() {
        return String.format("jdbc:mysql://%s:%d/%s", host, port, database);
    }
}

// 使用示例
DatabaseConfig config = new DatabaseConfig(
    "localhost", 3306, "mydb", "root", "password", 10
);
System.out.println(config.getConnectionUrl()); // jdbc:mysql://localhost:3306/mydb
```

### 3.3 值对象（Value Objects）

```java
public record Email(String value) {
    public Email {
        if (value == null || !value.contains("@")) {
            throw new IllegalArgumentException("无效的邮箱地址");
        }
    }
    
    public String getDomain() {
        return value.substring(value.indexOf("@") + 1);
    }
    
    public String getLocalPart() {
        return value.substring(0, value.indexOf("@"));
    }
}

public record PhoneNumber(String countryCode, String number) {
    public PhoneNumber {
        if (countryCode == null || countryCode.trim().isEmpty()) {
            throw new IllegalArgumentException("国家代码不能为空");
        }
        if (number == null || number.trim().isEmpty()) {
            throw new IllegalArgumentException("电话号码不能为空");
        }
    }
    
    public String getFullNumber() {
        return "+" + countryCode + number;
    }
}
```

### 3.4 事件对象

```java
public record UserRegisteredEvent(
    Long userId,
    String username,
    String email,
    LocalDateTime registeredAt
) implements DomainEvent {
    
    public UserRegisteredEvent {
        if (userId == null || userId <= 0) {
            throw new IllegalArgumentException("用户ID必须为正数");
        }
        if (registeredAt == null) {
            registeredAt = LocalDateTime.now();
        }
    }
}

public record OrderCreatedEvent(
    String orderId,
    String customerId,
    BigDecimal totalAmount,
    LocalDateTime createdAt
) implements DomainEvent {}
```

### 3.5 查询结果对象

```java
public record UserStatistics(
    long totalUsers,
    long activeUsers,
    long inactiveUsers,
    double averageAge,
    LocalDate reportDate
) {
    public double getActiveUserRatio() {
        return totalUsers > 0 ? (double) activeUsers / totalUsers : 0.0;
    }
}

public record SalesReport(
    String productName,
    int quantitySold,
    BigDecimal totalRevenue,
    LocalDate reportDate
) {
    public BigDecimal getAveragePrice() {
        return quantitySold > 0 ? totalRevenue.divide(BigDecimal.valueOf(quantitySold), 2, RoundingMode.HALF_UP) : BigDecimal.ZERO;
    }
}
```

## 4. Record 与传统类的对比

### 4.1 传统类实现

```java
public class PersonTraditional {
    private final String name;
    private final int age;
    
    public PersonTraditional(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        PersonTraditional that = (PersonTraditional) obj;
        return age == that.age && Objects.equals(name, that.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
    
    @Override
    public String toString() {
        return "PersonTraditional{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }
}
```

### 4.2 Record 实现

```java
public record PersonRecord(String name, int age) {}
```

**对比结果：**
- 传统类：47 行代码
- Record：1 行代码
- 功能完全相同，但 Record 更简洁

## 5. Record 的限制和注意事项

### 5.1 Record 的限制

```java
// ❌ Record 不能继承其他类
public record MyRecord(String value) extends SomeClass {} // 编译错误

// ❌ Record 不能声明实例字段
public record MyRecord(String value) {
    private String extraField; // 编译错误
}

// ❌ Record 不能声明实例初始化块
public record MyRecord(String value) {
    {
        System.out.println("初始化块"); // 编译错误
    }
}

// ❌ Record 不能声明 native 方法
public record MyRecord(String value) {
    public native void nativeMethod(); // 编译错误
}
```

### 5.2 何时不使用 Record

```java
// ❌ 需要可变状态的情况
public class Counter {
    private int count = 0;
    
    public void increment() {
        count++;
    }
    
    public int getCount() {
        return count;
    }
}

// ❌ 需要继承的情况
public abstract class Animal {
    public abstract void makeSound();
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("汪汪");
    }
}

// ❌ 需要复杂初始化逻辑的情况
public class DatabaseConnection {
    private Connection connection;
    
    public DatabaseConnection(String url, String username, String password) {
        try {
            this.connection = DriverManager.getConnection(url, username, password);
            // 复杂的初始化逻辑
        } catch (SQLException e) {
            throw new RuntimeException("数据库连接失败", e);
        }
    }
}
```

## 6. Record 最佳实践

### 6.1 命名规范

```java
// ✅ 好的命名
public record UserInfo(String name, String email) {}
public record ApiResponse<T>(boolean success, T data) {}
public record DatabaseConfig(String host, int port) {}

// ❌ 避免的命名
public record User(String name, String email) {} // 太通用
public record Data(String value) {} // 太模糊
```

### 6.2 验证和规范化

```java
public record Email(String value) {
    public Email {
        if (value == null || !isValidEmail(value)) {
            throw new IllegalArgumentException("无效的邮箱地址: " + value);
        }
        value = value.toLowerCase().trim();
    }
    
    private static boolean isValidEmail(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})$");
    }
}
```

### 6.3 文档和注释

```java
/**
 * 表示一个用户的基本信息
 * 
 * @param id 用户唯一标识符
 * @param name 用户姓名，不能为空
 * @param email 用户邮箱地址，必须是有效的邮箱格式
 * @param age 用户年龄，必须在0-150之间
 */
public record UserInfo(
    Long id,
    String name,
    Email email,
    int age
) {
    public UserInfo {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("姓名不能为空");
        }
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("年龄必须在0-150之间");
        }
    }
}
```

## 7. Record 在 Spring 中的应用

### 7.1 配置属性

```java
@ConfigurationProperties(prefix = "app")
public record AppConfig(
    String name,
    String version,
    DatabaseConfig database,
    RedisConfig redis
) {}

public record DatabaseConfig(
    String host,
    int port,
    String database,
    String username,
    String password
) {}

public record RedisConfig(
    String host,
    int port,
    String password,
    int timeout
) {}
```

### 7.2 API 响应对象

```java
@RestController
public class UserController {
    
    @GetMapping("/users/{id}")
    public ApiResponse<UserInfo> getUser(@PathVariable Long id) {
        UserInfo user = userService.findById(id);
        return ApiResponse.success(user);
    }
    
    @PostMapping("/users")
    public ApiResponse<UserInfo> createUser(@RequestBody CreateUserRequest request) {
        UserInfo user = userService.create(request);
        return ApiResponse.success(user);
    }
}

public record CreateUserRequest(
    String name,
    String email,
    int age
) {}
```

## 8. 总结

### 8.1 Record 的优势

1. **代码简洁**：大幅减少样板代码
2. **不可变性**：天然线程安全
3. **类型安全**：编译时类型检查
4. **性能优化**：JVM 可以更好地优化
5. **自动生成**：自动生成常用方法

### 8.2 适用场景

- ✅ 数据传输对象（DTO）
- ✅ 配置对象
- ✅ 值对象（Value Objects）
- ✅ 事件对象
- ✅ 查询结果对象
- ✅ 简单的数据聚合

### 8.3 不适用场景

- ❌ 需要可变状态
- ❌ 需要继承其他类
- ❌ 需要复杂的初始化逻辑
- ❌ 需要 native 方法
- ❌ 需要实例字段

Record 是 Java 现代化的重要特性，它让代码更简洁、更安全、更易维护。在合适的场景下使用 Record，可以显著提高开发效率和代码质量。
