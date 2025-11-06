# Java微服务集成方案说明

## 一、核心问题解答

**问题**：数据新增、更新操作都是Java微服务提供的，是否需要将这些接口重新封装成LangGraph工具？

**答案**：**不需要重新封装Java服务**，只需要在Python工具函数中调用Java微服务的HTTP API接口即可。这是标准的微服务架构集成方式。

## 二、技术原理

### 2.1 LangGraph工具的本质

LangGraph的工具（Tool）本质上就是：
- **Python函数**（同步或异步）
- 使用 `@tool` 装饰器标记
- 函数内部可以执行**任何Python代码**，包括：
  - 调用HTTP API（Java微服务）
  - 数据库操作
  - 文件操作
  - 调用其他Python库
  - 等等

### 2.2 工具调用流程

```
用户对话 → LLM决策调用工具 → 执行Python工具函数 → 调用Java微服务HTTP API → 返回结果 → LLM生成回复
```

## 三、实现方案

### 3.1 标准实现模式

在Python工具函数中直接调用Java微服务的HTTP接口：

```python
import httpx
from langchain_core.tools import tool

@tool("create_appointment", description="创建复诊预约")
async def create_appointment(
    doctor_id: str,
    appointment_date: str,
    department: str,
    user_id: str
) -> str:
    """
    创建复诊预约（调用Java微服务）
    
    Args:
        doctor_id: 医生ID
        appointment_date: 预约日期
        department: 科室
        user_id: 用户ID
    
    Returns:
        str: 预约结果消息
    """
    try:
        # 调用Java微服务的HTTP API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://java-service:8080/api/appointment/create",  # Java微服务地址
                json={
                    "doctorId": doctor_id,
                    "appointmentDate": appointment_date,
                    "department": department,
                    "userId": user_id
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"  # 如果需要认证
                },
                timeout=10.0
            )
            
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            
            # 根据Java微服务返回的结果，构造友好的返回消息
            if result.get("success"):
                appointment_id = result.get("data", {}).get("appointmentId")
                return f"预约成功！预约编号：{appointment_id}，预约日期：{appointment_date}"
            else:
                return f"预约失败：{result.get('message', '未知错误')}"
                
    except httpx.HTTPError as e:
        logger.error(f"调用Java微服务失败: {e}")
        return f"预约服务暂时不可用，请稍后重试。错误：{str(e)}"
    except Exception as e:
        logger.error(f"创建预约时发生错误: {e}")
        return f"创建预约时发生错误：{str(e)}"
```

### 3.2 更新操作的示例

```python
@tool("update_appointment", description="更新复诊预约信息")
async def update_appointment(
    appointment_id: str,
    appointment_date: str = None,
    doctor_id: str = None,
    status: str = None
) -> str:
    """
    更新复诊预约（调用Java微服务）
    
    Args:
        appointment_id: 预约ID
        appointment_date: 新的预约日期（可选）
        doctor_id: 新的医生ID（可选）
        status: 新的状态（可选）
    
    Returns:
        str: 更新结果消息
    """
    try:
        # 构造更新数据（只包含提供的字段）
        update_data = {}
        if appointment_date:
            update_data["appointmentDate"] = appointment_date
        if doctor_id:
            update_data["doctorId"] = doctor_id
        if status:
            update_data["status"] = status
        
        if not update_data:
            return "请至少提供一项要更新的信息"
        
        # 调用Java微服务的PUT或PATCH接口
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://java-service:8080/api/appointment/{appointment_id}",
                json=update_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                timeout=10.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return f"预约更新成功！预约编号：{appointment_id}"
            else:
                return f"更新失败：{result.get('message', '未知错误')}"
                
    except httpx.HTTPError as e:
        logger.error(f"调用Java微服务失败: {e}")
        return f"更新服务暂时不可用，请稍后重试。错误：{str(e)}"
    except Exception as e:
        logger.error(f"更新预约时发生错误: {e}")
        return f"更新预约时发生错误：{str(e)}"
```

### 3.3 查询操作的示例

```python
@tool("query_appointment", description="查询复诊预约记录")
async def query_appointment(
    user_id: str,
    start_date: str = None,
    end_date: str = None,
    status: str = None
) -> str:
    """
    查询复诊预约记录（调用Java微服务）
    
    Args:
        user_id: 用户ID
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        status: 预约状态（可选）
    
    Returns:
        str: 查询结果，格式化的预约列表
    """
    try:
        # 构造查询参数
        params = {"userId": user_id}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if status:
            params["status"] = status
        
        # 调用Java微服务的GET接口
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://java-service:8080/api/appointment/query",
                params=params,
                headers={
                    "Authorization": f"Bearer {get_token()}"
                },
                timeout=10.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                appointments = result.get("data", {}).get("list", [])
                
                if not appointments:
                    return "未找到符合条件的预约记录"
                
                # 格式化返回结果
                result_lines = [f"找到 {len(appointments)} 条预约记录：\n"]
                for idx, apt in enumerate(appointments, 1):
                    result_lines.append(
                        f"{idx}. 预约编号：{apt.get('appointmentId')}，"
                        f"医生：{apt.get('doctorName')}，"
                        f"日期：{apt.get('appointmentDate')}，"
                        f"状态：{apt.get('status')}"
                    )
                
                return "\n".join(result_lines)
            else:
                return f"查询失败：{result.get('message', '未知错误')}"
                
    except httpx.HTTPError as e:
        logger.error(f"调用Java微服务失败: {e}")
        return f"查询服务暂时不可用，请稍后重试。错误：{str(e)}"
    except Exception as e:
        logger.error(f"查询预约时发生错误: {e}")
        return f"查询预约时发生错误：{str(e)}"
```

## 四、架构优势

### 4.1 不需要重新封装的原因

1. **语言无关性**
   - HTTP是语言无关的协议
   - Python工具函数可以直接调用任何语言的HTTP服务
   - 不需要重新实现Java服务

2. **微服务架构标准实践**
   - 微服务之间通过HTTP/REST API通信
   - Python Agent和Java服务是独立的微服务
   - 保持服务解耦和独立部署

3. **职责分离**
   - Java微服务：负责业务逻辑和数据持久化
   - Python工具：负责AI对话和调用Java服务
   - 各司其职，互不干扰

### 4.2 这种方案的优点

1. **复用现有服务**
   - 直接使用现有的Java微服务
   - 不需要重复开发
   - 保持业务逻辑的一致性

2. **易于维护**
   - Java服务逻辑集中在一个地方
   - 修改业务逻辑只需要修改Java服务
   - Python工具只是调用层

3. **性能可控**
   - Java服务可以独立优化
   - 可以独立扩展和负载均衡
   - 不影响Python Agent的性能

4. **技术栈灵活**
   - Java服务可以用任何技术栈
   - Python Agent可以用任何Python库
   - 互不依赖

## 五、实际架构示例

### 5.1 完整架构图

```
┌─────────────────────────────────────────────────────────┐
│              Python Agent服务 (FastAPI)                  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         LangGraph Agent (Python)                   │ │
│  │                                                      │ │
│  │  ┌──────────────┐  ┌──────────────┐               │ │
│  │  │ 路由智能体    │  │ 专门智能体    │               │ │
│  │  └──────┬───────┘  └──────┬───────┘               │ │
│  │         │                 │                        │ │
│  │         └─────────┬───────┘                        │ │
│  │                   │                                │ │
│  │            ┌──────▼──────┐                         │ │
│  │            │ Python工具   │                         │ │
│  │            │ (调用HTTP)   │                         │ │
│  │            └──────┬───────┘                         │ │
│  └──────────────────┼──────────────────────────────────┘ │
└──────────────────────┼────────────────────────────────────┘
                       │ HTTP/REST API
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Java微服务集群 (Spring Boot)                     │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 复诊服务      │  │ 病历服务      │  │ 处方服务      │  │
│  │ (Java)        │  │ (Java)        │  │ (Java)        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ MySQL数据库   │  │ Redis缓存    │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 工具实现目录结构

```
utils/
├── tools/
│   ├── __init__.py
│   ├── router_tools.py              # 路由工具（内部逻辑）
│   ├── appointment_tools.py          # 复诊工具（调用Java服务）
│   │   ├── create_appointment()      # → POST /api/appointment/create
│   │   ├── update_appointment()      # → PUT /api/appointment/{id}
│   │   ├── query_appointment()       # → GET /api/appointment/query
│   │   └── cancel_appointment()      # → DELETE /api/appointment/{id}
│   │
│   ├── doctor_assistant_tools.py     # 医生助手工具（调用Java服务）
│   │   ├── query_patient_record()    # → GET /api/patient/record
│   │   ├── update_patient_record()   # → PUT /api/patient/record/{id}
│   │   ├── prescribe_medicine()       # → POST /api/prescription/create
│   │   └── query_prescription()      # → GET /api/prescription/query
│   │
│   └── blood_pressure_tools.py       # 血压工具（可能直接操作PostgreSQL）
│       ├── record_blood_pressure()   # → 直接操作PostgreSQL Store
│       └── query_blood_pressure()   # → 直接操作PostgreSQL Store
```

## 六、配置管理

### 6.1 Java微服务地址配置

在 `utils/config.py` 中配置Java微服务地址：

```python
class Config:
    # ... 其他配置 ...
    
    # Java微服务地址配置
    JAVA_SERVICE_BASE_URL = os.getenv(
        "JAVA_SERVICE_BASE_URL", 
        "http://java-service:8080"
    )
    
    # Java微服务认证配置
    JAVA_SERVICE_API_KEY = os.getenv("JAVA_SERVICE_API_KEY", "")
    JAVA_SERVICE_TIMEOUT = 10.0  # HTTP请求超时时间（秒）
```

### 6.2 HTTP客户端封装

可以创建一个通用的HTTP客户端工具类：

```python
# utils/http_client.py
import httpx
from typing import Dict, Any, Optional
from .config import Config

class JavaServiceClient:
    """Java微服务HTTP客户端"""
    
    def __init__(self):
        self.base_url = Config.JAVA_SERVICE_BASE_URL
        self.timeout = Config.JAVA_SERVICE_TIMEOUT
        self.api_key = Config.JAVA_SERVICE_API_KEY
    
    async def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST请求"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET请求"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT请求"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}{path}",
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def delete(self, path: str) -> Dict[str, Any]:
        """DELETE请求"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}{path}",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

# 全局客户端实例
java_client = JavaServiceClient()
```

然后在工具中使用：

```python
from utils.http_client import java_client

@tool("create_appointment", description="创建复诊预约")
async def create_appointment(doctor_id: str, appointment_date: str, ...) -> str:
    try:
        result = await java_client.post(
            "/api/appointment/create",
            {
                "doctorId": doctor_id,
                "appointmentDate": appointment_date,
                ...
            }
        )
        # ... 处理结果 ...
    except Exception as e:
        # ... 错误处理 ...
```

## 七、错误处理和重试

### 7.1 增加重试机制

```python
import asyncio
from typing import Callable, Any

async def retry_http_call(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Any:
    """HTTP调用重试装饰器"""
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay * (attempt + 1))
    raise Exception("重试次数用尽")

# 使用示例
@tool("create_appointment", description="创建复诊预约")
async def create_appointment(...) -> str:
    async def _call():
        return await java_client.post("/api/appointment/create", {...})
    
    try:
        result = await retry_http_call(_call, max_retries=3)
        # ... 处理结果 ...
    except Exception as e:
        # ... 错误处理 ...
```

## 八、总结

### 8.1 关键要点

1. **不需要重新封装Java服务**
   - LangGraph工具就是Python函数
   - 在函数内部调用Java微服务的HTTP API即可
   - 这是标准的微服务集成方式

2. **实现方式**
   - 使用 `httpx` 或 `aiohttp` 等异步HTTP客户端库
   - 在工具函数中调用Java微服务的REST API
   - 处理返回结果并转换为友好的消息

3. **架构优势**
   - 复用现有Java服务
   - 保持服务解耦
   - 易于维护和扩展

### 8.2 对设计方案的影响

**不需要修改设计方案**，因为：

1. 设计方案中的工具接口是通用的
2. 工具内部实现可以是：
   - 调用Java微服务（HTTP API）
   - 直接操作数据库（PostgreSQL）
   - 调用其他Python服务
   - 任何Python能做的事情

3. 这种实现方式完全符合设计方案
4. 只需要在具体实现时：
   - 确定哪些工具调用Java服务
   - 确定Java服务的API地址和格式
   - 实现HTTP客户端封装

### 8.3 实施建议

1. **第一步**：确定需要调用哪些Java微服务API
2. **第二步**：创建HTTP客户端封装类（可选，但推荐）
3. **第三步**：在工具函数中调用Java服务API
4. **第四步**：处理错误和异常情况
5. **第五步**：测试集成

---

*文档版本：v1.0*  
*更新时间：2025年11月*  
*作者：@舒小龙*

