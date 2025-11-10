# LangChain Python 模块详解

## 目录
1. [概述](#概述)
2. [核心包结构](#核心包结构)
3. [langchain-core 核心模块](#langchain-core-核心模块)
4. [langchain 主库模块](#langchain-主库模块)
5. [langchain-community 社区模块](#langchain-community-社区模块)
6. [langchain-openai OpenAI集成](#langchain-openai-openai集成)
7. [其他重要包](#其他重要包)
8. [项目中的实际使用](#项目中的实际使用)
9. [最佳实践](#最佳实践)

---

## 概述

LangChain 是一个用于开发由大型语言模型（LLM）驱动的应用程序的框架。它提供了模块化的组件和工具，帮助开发者构建具有上下文感知和推理能力的应用程序。

### 核心特点
- **模块化设计**：将复杂功能拆分为独立、可复用的组件
- **声明式编程**：使用 LangChain 表达式语言（LCEL）声明性地组合链式操作
- **丰富的集成**：支持多种 LLM 提供商、数据存储、工具和服务
- **生产就绪**：提供部署、监控和调试工具

---

## 核心包结构

LangChain Python 生态系统主要由以下核心包组成：

### 1. **langchain-core** (核心基础库)
- **作用**：提供基础抽象和核心接口
- **版本要求**：需与其他包版本匹配（如 0.3.x 与 langchain 0.3.x 匹配）

### 2. **langchain** (主库)
- **作用**：提供高级组件（链、代理、检索策略等）
- **版本要求**：0.3.x 与 langgraph 0.x 兼容

### 3. **langchain-community** (社区扩展)
- **作用**：包含第三方服务和工具的集成组件

### 4. **langchain-openai** (OpenAI 集成)
- **作用**：提供 OpenAI 兼容接口支持（包括 DeepSeek 等）

### 5. **langgraph** (图工作流)
- **作用**：用于构建状态图和智能体工作流
- **注意**：langgraph 1.0+ 版本 API 发生变化，0.x 版本与 langchain 0.3.x 兼容

---

## langchain-core 核心模块

`langchain-core` 是 LangChain 的基础库，提供了所有核心抽象和接口。

### 3.1 消息类型 (Messages)

**位置**：`langchain_core.messages`

**功能**：定义不同类型的消息，用于 LLM 对话

**主要类**：
- `BaseMessage`：所有消息的基类
- `HumanMessage`：用户消息
- `AIMessage`：AI 助手消息
- `SystemMessage`：系统提示消息
- `FunctionMessage`：函数调用结果消息
- `ToolMessage`：工具执行结果消息

**使用示例**：
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 用户消息
user_msg = HumanMessage(content="你好，我想记录血压")

# AI 消息
ai_msg = AIMessage(content="好的，请告诉我您的血压值")

# 系统消息
system_msg = SystemMessage(content="你是一个医疗助手")
```

**项目中的使用**：
- `utils/router.py`：使用 `HumanMessage` 和 `AIMessage` 处理对话
- `utils/router_state.py`：使用 `BaseMessage` 定义状态中的消息类型
- `01_backendServer.py`：在 API 层处理消息转换

### 3.2 工具系统 (Tools)

**位置**：`langchain_core.tools`

**功能**：定义可被 LLM 调用的工具函数

**主要组件**：
- `@tool` 装饰器：将 Python 函数转换为 LangChain 工具
- `BaseTool`：工具基类
- `Tool`：工具类

**使用示例**：
```python
from langchain_core.tools import tool

@tool("create_appointment", description="创建复诊预约")
async def create_appointment(
    doctor_id: str,
    appointment_date: str,
    department: str,
    user_id: str
) -> str:
    """创建复诊预约的工具函数"""
    # 实现预约创建逻辑
    return f"预约已创建：{appointment_date}"
```

**项目中的使用**：
- `utils/tools/appointment_tools.py`：复诊管理工具
- `utils/tools/blood_pressure_tools.py`：血压记录工具
- `utils/tools/diagnosis_tools.py`：诊断工具
- `utils/tools/router_tools.py`：路由工具

### 3.3 提示模板 (Prompts)

**位置**：`langchain_core.prompts`

**功能**：定义和管理提示模板

**主要类**：
- `ChatPromptTemplate`：聊天提示模板
- `PromptTemplate`：基础提示模板
- `MessagesPlaceholder`：消息占位符

**使用示例**：
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个医疗助手"),
    ("human", "{user_input}")
])
```

**项目中的使用**：
- `utils/tools/appointment_tools.py`：使用 `ChatPromptTemplate` 构建提示
- `utils/tools/blood_pressure_tools.py`：构建血压记录提示
- `utils/tools/router_tools.py`：构建路由决策提示

### 3.4 语言模型接口 (Language Models)

**位置**：`langchain_core.language_models`

**功能**：定义 LLM 的标准接口

**主要类**：
- `BaseChatModel`：聊天模型的基类
- `BaseLLM`：基础 LLM 接口
- `ChatModel`：聊天模型接口

**使用示例**：
```python
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm() -> BaseChatModel:
    # 初始化并返回 LLM 实例
    pass
```

**项目中的使用**：
- `utils/llms.py`：使用 `BaseChatModel` 作为返回类型
- `utils/agents/*.py`：所有智能体都使用 `BaseChatModel` 接口

### 3.5 运行配置 (Runnables)

**位置**：`langchain_core.runnables`

**功能**：提供可运行组件的基类和工具

**主要组件**：
- `Runnable`：可运行组件的基类
- `RunnableConfig`：运行配置
- `RunnableLambda`：将函数转换为可运行组件

### 3.6 输出解析器 (Output Parsers)

**位置**：`langchain_core.output_parsers`

**功能**：解析 LLM 输出为结构化数据

**主要类**：
- `BaseOutputParser`：输出解析器基类
- `StrOutputParser`：字符串输出解析器
- `JsonOutputParser`：JSON 输出解析器
- `PydanticOutputParser`：Pydantic 模型输出解析器

---

## langchain 主库模块

`langchain` 主库提供了高级组件和现成的实现。

### 4.1 聊天模型初始化

**位置**：`langchain.chat_models`

**功能**：提供统一的 LLM 初始化接口

**主要函数**：
- `init_chat_model()`：初始化聊天模型（支持多种提供商）

**使用示例**：
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="openai:deepseek-chat",
    temperature=0,
    base_url="https://api.deepseek.com",
    api_key="your-api-key"
)
```

**项目中的使用**：
- `utils/llms.py`：使用 `init_chat_model` 初始化 DeepSeek 模型

### 4.2 文本分割器 (Text Splitters)

**位置**：`langchain.text_splitter`

**功能**：将长文本分割为适合处理的块

**主要类**：
- `RecursiveCharacterTextSplitter`：递归字符分割器（最常用）
- `CharacterTextSplitter`：字符分割器
- `TokenTextSplitter`：按 token 分割
- `MarkdownHeaderTextSplitter`：Markdown 标题分割器

**使用示例**：
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)

chunks = splitter.split_text(long_text)
```

**项目中的使用**：
- `utils/rag/text_splitter.py`：封装了文本分割功能
- `test/rag_env_check/test_rag_infrastructure.py`：测试中使用

### 4.3 文档加载器 (Document Loaders)

**位置**：`langchain.document_loaders`

**功能**：从各种来源加载文档

**主要类**：
- `TextLoader`：文本文件加载器
- `PDFLoader`：PDF 文件加载器
- `DirectoryLoader`：目录加载器
- `WebBaseLoader`：网页加载器
- `CSVLoader`：CSV 文件加载器

### 4.4 链 (Chains)

**位置**：`langchain.chains`

**功能**：将多个组件组合成链式操作

**主要类**：
- `LLMChain`：基础 LLM 链
- `ConversationChain`：对话链
- `RetrievalQAChain`：检索增强问答链
- `MapReduceChain`：映射归约链

**注意**：在 LangChain 0.3+ 版本中，推荐使用 LCEL（LangChain Expression Language）而不是传统的 Chain 类。

### 4.5 代理 (Agents)

**位置**：`langchain.agents`

**功能**：提供智能体实现

**主要组件**：
- `AgentExecutor`：代理执行器
- `create_react_agent`：创建 ReAct 代理
- `AgentType`：代理类型枚举

**注意**：在 LangGraph 架构中，代理通常通过 StateGraph 实现，而不是传统的 Agent 类。

### 4.6 检索器 (Retrievers)

**位置**：`langchain.retrievers`

**功能**：从向量存储中检索相关文档

**主要类**：
- `BaseRetriever`：检索器基类
- `VectorStoreRetriever`：向量存储检索器
- `ContextualCompressionRetriever`：上下文压缩检索器

### 4.7 记忆 (Memory)

**位置**：`langchain.memory`

**功能**：管理对话历史记忆

**主要类**：
- `ConversationBufferMemory`：对话缓冲记忆
- `ConversationBufferWindowMemory`：窗口记忆
- `ConversationSummaryMemory`：摘要记忆

**注意**：在 LangGraph 中，记忆通过状态管理和检查点（Checkpoint）实现。

---

## langchain-community 社区模块

`langchain-community` 包含与第三方服务和工具的集成。

### 5.1 向量存储 (Vector Stores)

**位置**：`langchain_community.vectorstores`

**功能**：与各种向量数据库集成

**支持的向量存储**：
- `PGVector`：PostgreSQL + pgvector
- `Chroma`：Chroma 向量数据库
- `FAISS`：Facebook AI Similarity Search
- `Pinecone`：Pinecone 向量数据库
- `Weaviate`：Weaviate 向量数据库
- `Milvus`：Milvus 向量数据库
- `Qdrant`：Qdrant 向量数据库

**使用示例**：
```python
from langchain_community.vectorstores import PGVector

vector_store = PGVector(
    connection_string=connection_string,
    embedding_function=embedding_function,
    collection_name="documents"
)
```

### 5.2 嵌入模型 (Embeddings)

**位置**：`langchain_community.embeddings`

**功能**：与各种嵌入模型提供商集成

**支持的嵌入模型**：
- `OpenAIEmbeddings`：OpenAI 嵌入模型
- `HuggingFaceEmbeddings`：HuggingFace 模型
- `SentenceTransformerEmbeddings`：Sentence Transformers
- `CohereEmbeddings`：Cohere 嵌入模型

### 5.3 LLM 提供商集成

**位置**：`langchain_community.llms`

**功能**：与各种 LLM 提供商集成

**支持的提供商**：
- `HuggingFacePipeline`：HuggingFace 模型
- `Ollama`：本地 Ollama 模型
- `Anthropic`：Anthropic Claude
- `Google`：Google PaLM/Gemini
- `AzureOpenAI`：Azure OpenAI

### 5.4 工具集成

**位置**：`langchain_community.tools`

**功能**：提供各种现成的工具

**可用工具**：
- `DuckDuckGoSearchRun`：网络搜索
- `WikipediaQueryRun`：维基百科查询
- `ShellTool`：Shell 命令执行
- `PythonREPLTool`：Python REPL
- `FileManagementTool`：文件管理

### 5.5 文档加载器扩展

**位置**：`langchain_community.document_loaders`

**功能**：扩展的文档加载器

**支持的格式**：
- `PyPDFLoader`：PDF 文件
- `UnstructuredFileLoader`：非结构化文件
- `SeleniumURLLoader`：使用 Selenium 加载网页
- `GitLoader`：Git 仓库加载器

---

## langchain-openai OpenAI集成

`langchain-openai` 提供 OpenAI 兼容接口支持。

### 6.1 聊天模型

**位置**：`langchain_openai`

**功能**：OpenAI 格式的聊天模型接口

**主要类**：
- `ChatOpenAI`：OpenAI 聊天模型（兼容接口）

**使用场景**：
- 使用 DeepSeek、OpenAI 等兼容 OpenAI API 的模型
- 通过 `init_chat_model()` 统一初始化

**项目中的使用**：
- `utils/llms.py`：使用 `init_chat_model` 初始化 DeepSeek 模型（OpenAI 兼容接口）

---

## 其他重要包

### 7.1 langgraph

**位置**：`langgraph`

**功能**：构建状态图和智能体工作流

**主要组件**：
- `StateGraph`：状态图构建器
- `MessageGraph`：消息图（简化版）
- `checkpoint`：检查点系统（状态持久化）
- `store`：存储系统

**项目中的使用**：
- `utils/router_graph.py`：使用 `StateGraph` 构建路由图
- `01_backendServer.py`：使用 `AsyncPostgresSaver` 和 `AsyncPostgresStore` 进行状态持久化

### 7.2 langgraph-checkpoint-postgres

**位置**：`langgraph.checkpoint.postgres`

**功能**：PostgreSQL 检查点和存储支持

**主要组件**：
- `AsyncPostgresSaver`：异步 PostgreSQL 检查点保存器
- `AsyncPostgresStore`：异步 PostgreSQL 存储

**项目中的使用**：
- `01_backendServer.py`：用于持久化智能体状态

### 7.3 langgraph-prebuilt

**位置**：`langgraph.prebuilt`

**功能**：预构建的智能体组件

**主要组件**：
- `create_react_agent`：创建 ReAct 智能体

---

## 项目中的实际使用

### 8.1 LLM 初始化

**文件**：`utils/llms.py`

**使用的模块**：
- `langchain.chat_models.init_chat_model`
- `langchain_core.language_models.chat_models.BaseChatModel`

**功能**：
- 统一的 LLM 初始化接口
- 支持 DeepSeek 等 OpenAI 兼容模型
- 配置管理和错误处理

### 8.2 工具定义

**文件**：`utils/tools/*.py`

**使用的模块**：
- `langchain_core.tools.tool` 装饰器
- `langchain_core.prompts.ChatPromptTemplate`

**功能**：
- 定义可被 LLM 调用的工具函数
- 血压记录、复诊管理、诊断等业务工具
- 使用提示模板优化工具调用

### 8.3 路由图构建

**文件**：`utils/router_graph.py`

**使用的模块**：
- `langgraph.graph.StateGraph`
- `langgraph.checkpoint.postgres.aio.AsyncPostgresSaver`
- `langchain_core.messages.AIMessage`

**功能**：
- 构建多智能体路由系统
- 状态管理和持久化
- 消息传递和处理

### 8.4 RAG 功能

**文件**：`utils/rag/*.py`

**使用的模块**：
- `langchain.text_splitter.RecursiveCharacterTextSplitter`

**功能**：
- 文档加载和分割
- 向量化和存储
- 检索增强生成

### 8.5 智能体实现

**文件**：`utils/agents/*.py`

**使用的模块**：
- `langchain_core.language_models.chat_models.BaseChatModel`
- `langchain_core.messages.SystemMessage`

**功能**：
- 血压记录智能体
- 复诊管理智能体
- 诊断智能体

---

## 最佳实践

### 9.1 版本兼容性

**重要提示**：
- `langchain 0.3.x` 与 `langgraph 0.x` 兼容
- `langchain 1.0+` 与 `langgraph 0.x` **不兼容**
- `langgraph 1.0+` 版本 API 发生变化
- 所有相关包版本需保持一致

**项目配置**：
```python
langgraph>=0.2.0,<1.0.0
langchain>=0.3.0,<1.0.0
langchain-core>=0.3.0,<1.0.0
langchain-openai>=0.2.0,<0.3.0
langchain-community>=0.3.0,<1.0.0
```

### 9.2 使用 LCEL 而非传统 Chains

**推荐做法**：
```python
# ✅ 推荐：使用 LCEL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_messages([("human", "{input}")])
    | llm
    | StrOutputParser()
)

# ❌ 不推荐：使用传统 Chain 类（已过时）
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
```

### 9.3 工具定义最佳实践

**推荐做法**：
```python
from langchain_core.tools import tool

@tool("tool_name", description="清晰的工具描述")
async def tool_function(
    param1: str,  # 使用类型提示
    param2: int
) -> str:
    """
    详细的工具文档字符串
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        返回值说明
    """
    # 实现逻辑
    return result
```

### 9.4 消息处理最佳实践

**推荐做法**：
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 构建消息列表
messages = [
    SystemMessage(content="系统提示"),
    HumanMessage(content="用户输入"),
    AIMessage(content="AI 回复")
]

# 在状态中管理消息
state = {
    "messages": messages
}
```

### 9.5 错误处理

**推荐做法**：
```python
from langchain_core.language_models.chat_models import BaseChatModel

class LLMInitializationError(Exception):
    """自定义异常类"""
    pass

def get_llm() -> BaseChatModel:
    try:
        llm = init_chat_model(...)
        return llm
    except Exception as e:
        raise LLMInitializationError(f"初始化失败: {str(e)}") from e
```

### 9.6 状态管理

**在 LangGraph 中**：
- 使用 `StateGraph` 管理状态
- 通过检查点系统持久化状态
- 使用类型化的状态类（如 `RouterState`）

**推荐做法**：
```python
from langgraph.graph import StateGraph
from typing import TypedDict
from langchain_core.messages import BaseMessage

class RouterState(TypedDict):
    messages: list[BaseMessage]
    current_intent: str

graph = StateGraph(RouterState)
```

---

## 总结

LangChain Python 提供了丰富的模块和组件，支持构建复杂的 LLM 应用程序：

1. **核心基础**：`langchain-core` 提供所有基础抽象
2. **高级功能**：`langchain` 提供现成的链、代理等组件
3. **扩展集成**：`langchain-community` 提供第三方服务集成
4. **工作流**：`langgraph` 提供状态图和工作流支持
5. **生产工具**：LangServe、LangSmith 支持部署和监控

在项目中使用时，需要注意版本兼容性，优先使用 LCEL 和现代 API，遵循最佳实践以确保代码的可维护性和可扩展性。

---

## 参考资料

- [LangChain 官方文档](https://python.langchain.com/)
- [LangChain 中文文档](https://python.langchain.com.cn/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [项目 requirements.txt](../V2_0_Agent/requirements.txt)

---

**文档创建时间**：2025-02-01  
**最后更新**：2025-02-01  
**适用版本**：LangChain 0.3.x, LangGraph 0.x

