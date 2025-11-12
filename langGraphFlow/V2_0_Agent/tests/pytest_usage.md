# pytest 使用指南

本文档详细介绍如何使用 pytest 运行测试。

## 执行目录

**重要**：所有 pytest 命令必须在项目根目录（`V2_0_Agent/`）下执行，而不是在 `tests/` 目录下。

```bash
# 正确的执行目录
cd /path/to/V2_0_Agent

# 错误的执行目录（不要在这里执行）
cd /path/to/V2_0_Agent/tests  # ❌ 不要在这里执行
```

## 基本执行命令

### 1. 运行所有测试

```bash
# 在项目根目录下执行
conda run -n py_311_rag python -m pytest

# 或者使用 pytest 命令（如果已安装）
conda run -n py_311_rag pytest
```

### 2. 运行特定类型的测试

```bash
# 运行所有单元测试
conda run -n py_311_rag python -m pytest tests/unit/

# 运行所有集成测试
conda run -n py_311_rag python -m pytest tests/integration/

# 运行所有端到端测试
conda run -n py_311_rag python -m pytest tests/e2e/
```

### 3. 运行特定测试文件

```bash
# 运行单个测试文件
conda run -n py_311_rag python -m pytest tests/unit/db_models/test_db_models.py

# 运行特定目录下的所有测试
conda run -n py_311_rag python -m pytest tests/unit/router/

# 运行 core 目录下的所有测试文件（示例）
conda run -n py_311_rag python -m pytest tests/unit/core/
```

### 4. 运行特定测试函数

```bash
# 运行特定测试函数
conda run -n py_311_rag python -m pytest tests/unit/db_models/test_db_models.py::test_models

# 运行匹配模式的测试
conda run -n py_311_rag python -m pytest -k "test_models"
```

### 5. 使用测试标记

```bash
# 运行标记为 unit 的测试
conda run -n py_311_rag python -m pytest -m unit

# 运行标记为 integration 的测试
conda run -n py_311_rag python -m pytest -m integration

# 运行需要数据库的测试
conda run -n py_311_rag python -m pytest -m requires_db

# 排除慢速测试
conda run -n py_311_rag python -m pytest -m "not slow"
```

### 6. 输出选项

```bash
# 详细输出（-v 或 --verbose）
conda run -n py_311_rag python -m pytest -v

# 显示打印输出（-s 或 --capture=no）- 实时显示 print 语句
conda run -n py_311_rag python -m pytest -s

# 显示最详细的输出（-vv）
conda run -n py_311_rag python -m pytest -vv

# 显示失败测试的详细信息
conda run -n py_311_rag python -m pytest --tb=long

# 实时显示执行进度（推荐用于长时间运行的测试）
# 注意：log_cli 已在 pytest.ini 中配置，无需在命令行指定
conda run -n py_311_rag python -m pytest -s

# 实时显示执行进度 + 详细输出（推荐）
conda run -n py_311_rag python -m pytest -sv

# 实时显示执行进度 + 最详细输出
conda run -n py_311_rag python -m pytest -svv

# 实时显示执行进度 + 显示测试名称（推荐）
conda run -n py_311_rag python -m pytest -sv --tb=short

# 实时显示执行进度 + 自定义日志级别和格式
conda run -n py_311_rag python -m pytest -sv --log-cli-level=INFO --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
```

### 7. 直接运行测试脚本（不使用 pytest）

某些测试文件可以直接运行（不依赖 pytest）：

```bash
# 直接运行测试脚本
conda run -n py_311_rag python tests/unit/db_models/test_db_models.py
conda run -n py_311_rag python tests/unit/core/test_config.py
```

## 配置文件说明

项目已配置 `pytest.ini` 文件，位于项目根目录，包含以下默认配置：

- **测试目录**：`tests`
- **输出选项**：详细输出（-v）、简短错误追踪（--tb=short）、彩色输出、实时显示（-s）
- **测试标记**：unit、integration、e2e、slow、requires_db、requires_llm、requires_redis
- **日志配置**：DEBUG 级别日志输出，实时显示（log_cli = true, log_cli_level = DEBUG）
- **异步支持**：自动处理异步测试

**注意**：
- 默认配置已启用 `-s` 参数，会实时显示 print 输出
- 默认配置已启用 `log_cli = true` 和 `log_cli_level = DEBUG`，会实时显示所有日志（包括 DEBUG、INFO、WARNING、ERROR）
- 如果日志太多，可以在命令行使用 `--log-cli-level=INFO` 来只显示 INFO 及以上级别的日志

## 实时监控测试执行

**问题**：长时间运行的测试可能没有输出，不知道执行进度。

**解决方案**：使用以下命令实时显示执行情况：

```bash
# 方案1：实时显示 print 输出和日志（推荐，默认配置）
# 注意：log_cli 和 -s 已在 pytest.ini 中配置，会自动实时显示日志和 print 输出
conda run -n py_311_rag python -m pytest tests/unit/router/ -sv

# 方案2：实时显示 + DEBUG 级别日志（推荐，查看详细日志）
# 如果默认的 DEBUG 级别日志太多，可以改为 INFO
conda run -n py_311_rag python -m pytest tests/unit/router/ -sv --log-cli-level=DEBUG

# 方案3：实时显示 + INFO 级别日志（减少日志输出）
conda run -n py_311_rag python -m pytest tests/unit/router/ -sv --log-cli-level=INFO

# 方案4：实时显示 + 显示测试名称
conda run -n py_311_rag python -m pytest tests/unit/router/ -sv --tb=short

# 方案5：实时显示 + 最详细输出
conda run -n py_311_rag python -m pytest tests/unit/router/ -svv
```

**重要提示**：
- `-s` 或 `--capture=no`：禁用输出捕获，实时显示 print 语句（已在 pytest.ini 中配置）
- `log_cli = true`：启用实时日志输出（已在 pytest.ini 中配置）
- `log_cli_level = DEBUG`：默认日志级别为 DEBUG，会显示所有日志（包括 INFO、DEBUG 等）
- 如果日志太多，可以在命令行使用 `--log-cli-level=INFO` 来只显示 INFO 及以上级别的日志
- 日志会实时显示在 "live log call" 部分，与测试输出混合显示

**重要说明：pytest 日志输出机制**

pytest 的 `log_cli` 功能**确实支持实时日志输出**。当启用 `log_cli = true` 时，pytest 会在测试执行过程中实时显示日志。

**什么是 "live log call"**：

"live log call" 是 pytest 在输出中显示的一个**分隔标记**，用来标识"这是测试执行期间的实时日志输出"。当你看到这个标记时，说明下面的日志是在测试运行过程中实时输出的。

**输出示例**：
```
tests/unit/router/test_router.py::test_identify_intent_tool 
-------------------------------- live log call ---------------------------------
2025-11-12 11:48:58 [    INFO] core.llm.factory: LLM实例创建成功: model=openai:deepseek-chat, temperature=0.0
2025-11-12 11:48:58 [    INFO] core.llm.callbacks: [ChatModel请求开始] Run ID: a2664a9e-6cf3-4905-92cb-85c87a8eb2a5
2025-11-12 11:49:02 [    INFO] core.llm.callbacks: [LLM响应结束] Run ID: a2664a9e-6cf3-4905-92cb-85c87a8eb2a5
...
```

**如何确认日志是实时的**：
- 查看日志的时间戳，如果时间戳是连续的（例如从 11:48:58 到 11:49:35），说明日志是实时输出的
- 日志会在 "live log call" 标记下方实时显示，这是 pytest 的预期行为
- 这些日志与 `print()` 输出分开显示，`print()` 输出会直接显示在测试输出中，而日志会显示在 "live log call" 部分

**如果日志仍然不实时显示（最后才输出）**：

这可能是 Python 输出缓冲或终端缓冲导致的。尝试以下解决方案：

1. **使用 `-u` 参数禁用 Python 缓冲**（推荐）：
   ```bash
   conda run -n py_311_rag python -u -m pytest tests/unit/router/test_router.py -sv --log-cli-level=DEBUG
   ```

2. **设置环境变量 `PYTHONUNBUFFERED=1`**：
   ```bash
   PYTHONUNBUFFERED=1 conda run -n py_311_rag python -m pytest tests/unit/router/test_router.py -sv --log-cli-level=DEBUG
   ```

3. **确保在命令行明确指定日志级别**（即使配置文件中已设置）：
   ```bash
   conda run -n py_311_rag python -u -m pytest tests/unit/router/test_router.py -sv --log-cli-level=DEBUG
   ```

4. **检查日志输出位置**：日志会显示在 "live log call" 部分，这是正常的。如果看不到这个部分，说明日志可能被缓冲了。

5. **如果使用 IDE**：某些 IDE 可能会缓冲输出，建议在终端中直接运行命令。

**注意**：pytest 的 `log_cli` 功能本身是实时的，但可能受到以下因素影响：
- Python 的输出缓冲（使用 `-u` 参数可以解决）
- 终端的缓冲（某些终端可能会缓冲输出）
- IDE 的缓冲（如果使用 IDE 运行测试）

**确认配置已正确**：
- ✅ `log_cli = true` 已在 `pytest.ini` 中设置
- ✅ `log_cli_level = DEBUG` 已在 `pytest.ini` 中设置
- ✅ `-s` 参数已在 `pytest.ini` 的 `addopts` 中设置
- ✅ `--log-cli-level=DEBUG` 已在 `pytest.ini` 的 `addopts` 中设置

如果以上配置都已正确，日志应该会实时显示在 "live log call" 部分。

## 注意事项

1. **环境要求**：
   - 确保已激活正确的 conda 环境：`py_311_rag`
   - 确保已安装 pytest：`conda run -n py_311_rag pip install pytest>=7.0.0`

2. **前置条件**：
   - 单元测试：通常不需要外部依赖
   - 集成测试：需要数据库和 LLM API 配置
   - 端到端测试：需要完整的服务环境

3. **路径处理**：
   - 所有测试文件都已配置正确的路径处理（通过 `conftest.py` 和 `sys.path.insert`）
   - 确保从项目根目录执行，路径处理会自动生效

4. **测试隔离**：
   - 每个集成测试使用独立的 `user_id` 和 `session_id`，避免冲突
   - 测试会自动清理 checkpoint 和 store 数据

5. **实时监控**：
   - 默认配置已启用 `-s` 和 `log_cli = true`，会实时显示 print 输出和日志
   - 默认日志级别为 `DEBUG`，会显示所有日志；如果日志太多，可以使用 `--log-cli-level=INFO` 来减少输出
   - 日志会实时显示在 "live log call" 部分，与测试输出混合显示
   - 如果日志仍然不实时显示，可能是终端缓冲问题，尝试使用 `python -u` 或设置环境变量 `PYTHONUNBUFFERED=1`

## 常用命令示例

### 运行 core 目录下的所有测试

```bash
# 在项目根目录下执行
conda run -n py_311_rag python -m pytest tests/unit/core/ -sv
```

### 运行特定测试文件

```bash
# 运行 core 目录下的配置测试
conda run -n py_311_rag python -m pytest tests/unit/core/test_config.py -sv
```

### 运行匹配模式的测试

```bash
# 运行所有包含 "config" 的测试
conda run -n py_311_rag python -m pytest -k "config" -sv
```

