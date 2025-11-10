# 路由功能测试

本目录包含路由智能体的单元测试。

## 测试文件

- `test_router.py` - 路由功能单元测试
- `test_router_graph.py` - 路由图创建测试
- `test_clarify_intent.py` - 意图澄清功能测试

## 测试范围

- RouterState数据结构测试
- IntentResult数据结构测试
- identify_intent工具测试（意图识别）
- clarify_intent工具测试（意图澄清）
- route_decision函数测试（路由决策）
- 路由图创建测试（验证所有节点是否正确创建）
- 意图澄清功能完整性测试（验证澄清问题是否包含所有智能体功能）

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# 路由功能单元测试
conda run -n py_311_rag python test/router/test_router.py

# 路由图创建测试
conda run -n py_311_rag python test/router/test_router_graph.py

# 意图澄清功能测试
conda run -n py_311_rag python test/router/test_clarify_intent.py
```

## 测试特点

- **test_router.py**: 单元测试，不依赖数据库，测试路由核心逻辑
- **test_router_graph.py**: 集成测试，需要数据库连接，验证路由图结构完整性
- 验证意图识别准确性
- 验证路由决策正确性
- 验证所有智能体节点是否正确创建

## 前置条件

- LLM API配置正确（用于意图识别）
- 环境变量 `DEEPSEEK_API_KEY` 已设置

## 相关文档

- `V2.0-11-路由智能体详细设计.md` - 路由智能体详细设计
- `utils/router.py` - 路由节点实现
- `utils/tools/router_tools.py` - 路由工具实现

