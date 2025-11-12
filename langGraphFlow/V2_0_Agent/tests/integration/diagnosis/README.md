# 诊断智能体测试

本目录包含诊断智能体的集成测试用例。

## 测试文件

- `test_internal_medicine_diagnosis_integration.py` - 内科诊断智能体集成测试
- `test_multi_department_diagnosis.py` - 多科室诊断智能体集成测试

## 运行方式

```bash
cd langGraphFlow/V2_0_Agent

# 内科诊断智能体集成测试
conda run -n py_311_rag python tests/integration/diagnosis/test_internal_medicine_diagnosis_integration.py

# 多科室诊断智能体集成测试
conda run -n py_311_rag python tests/integration/diagnosis/test_multi_department_diagnosis.py
```

## 测试用例

### 1. 内科诊断智能体集成测试 (`test_internal_medicine_diagnosis_integration.py`)

**test_internal_medicine_diagnosis_agent**：内科诊断智能体集成测试
- 数据库连接测试：验证数据库连接池和checkpointer初始化
- 路由智能体创建测试：验证路由图创建成功
- 诊断意图识别测试：测试路由工具能否正确识别诊断意图
- 路由到诊断智能体测试：测试能否正确路由到内科诊断智能体
- RAG检索测试：测试诊断智能体能否调用RAG检索工具
- 端到端流程测试：测试完整的诊断流程（用户输入 -> 路由 -> 诊断智能体 -> RAG检索 -> 生成回复）
- 包含多个测试查询场景：
  - 高血压症状诊断
  - 冠心病诊断（胸痛、心悸）
  - 肺炎诊断（咳嗽、发热）

### 2. 多科室诊断智能体集成测试 (`test_multi_department_diagnosis.py`)

**test_diagnosis_system_prompts**：测试各科室系统提示词生成
- 验证各科室（内科、外科、儿科、妇科、心内科、全科）系统提示词是否正确生成
- 验证提示词包含科室信息和诊断相关内容

**test_diagnosis_agent_nodes**：测试各科室诊断智能体节点创建
- 验证各科室诊断智能体节点能否正确创建
- 验证节点配置和功能是否正常

## 前置条件

1. **Python环境**：conda环境 `py_311_rag` (Python 3.11)
2. **数据库**：PostgreSQL数据库（doctor_agent_db），已安装pgvector扩展
3. **知识库**：内科知识库已构建（运行 `scripts/build_internal_medicine_kb.py`）
4. **LLM API**：DeepSeek API Key，配置在环境变量 `DEEPSEEK_API_KEY` 中

## 注意事项

- 测试会创建测试会话，不会影响生产数据
- 测试需要调用LLM API，会产生API调用费用
- 确保知识库已构建，否则RAG检索会失败

