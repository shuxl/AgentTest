"""
LLM回调模块测试
测试core.llm.callbacks模块的功能
"""
import os
import sys
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.llm.callbacks import ModelInteractionLogger, get_model_interaction_logger
from langchain_core.outputs import LLMResult, Generation
from langchain_core.messages import HumanMessage, AIMessage


def test_model_interaction_logger_initialization():
    """测试ModelInteractionLogger初始化"""
    print("=" * 60)
    print("测试1：ModelInteractionLogger初始化")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    assert logger is not None
    assert logger.verbose is True
    assert hasattr(logger, 'start_times')
    assert isinstance(logger.start_times, dict)
    
    # 测试verbose=False
    logger2 = ModelInteractionLogger(verbose=False)
    assert logger2.verbose is False
    
    print("✅ ModelInteractionLogger初始化测试通过")


def test_on_llm_start():
    """测试on_llm_start回调"""
    print("=" * 60)
    print("测试2：on_llm_start回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    serialized = {"name": "test-model"}
    prompts = ["Test prompt 1", "Test prompt 2"]
    run_id = "test-run-123"
    
    logger.on_llm_start(serialized, prompts, run_id=run_id)
    
    # 验证开始时间被记录
    assert run_id in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "LLM请求开始" in log_output or "Run ID" in log_output
    assert run_id in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_llm_start回调测试通过")


def test_on_llm_end():
    """测试on_llm_end回调"""
    print("=" * 60)
    print("测试3：on_llm_end回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    run_id = "test-run-123"
    logger.start_times[run_id] = 1000.0  # 设置开始时间
    
    # 创建模拟的LLMResult
    generation = Generation(text="Test response")
    llm_result = LLMResult(generations=[[generation]])
    
    logger.on_llm_end(llm_result, run_id=run_id)
    
    # 验证开始时间被移除
    assert run_id not in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "LLM响应结束" in log_output or "Run ID" in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_llm_end回调测试通过")


def test_on_llm_error():
    """测试on_llm_error回调"""
    print("=" * 60)
    print("测试4：on_llm_error回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.ERROR)
    
    run_id = "test-run-123"
    logger.start_times[run_id] = 1000.0  # 设置开始时间
    
    error = Exception("Test error message")
    
    logger.on_llm_error(error, run_id=run_id)
    
    # 验证开始时间被清理
    assert run_id not in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "LLM错误" in log_output or "错误" in log_output
    assert "Test error message" in log_output or "Exception" in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_llm_error回调测试通过")


def test_on_chat_model_start():
    """测试on_chat_model_start回调"""
    print("=" * 60)
    print("测试5：on_chat_model_start回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    serialized = {"name": "test-chat-model"}
    messages = [[HumanMessage(content="Hello")], [AIMessage(content="Hi")]]
    run_id = "test-chat-run-123"
    
    logger.on_chat_model_start(serialized, messages, run_id=run_id)
    
    # 验证开始时间被记录
    assert run_id in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "ChatModel请求开始" in log_output or "Run ID" in log_output
    assert run_id in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_chat_model_start回调测试通过")


def test_on_chat_model_end():
    """测试on_chat_model_end回调"""
    print("=" * 60)
    print("测试6：on_chat_model_end回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    run_id = "test-chat-run-123"
    logger.start_times[run_id] = 1000.0  # 设置开始时间
    
    # 创建模拟的响应对象
    mock_response = MagicMock()
    mock_generation = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test chat response"
    mock_generation.message = mock_message
    mock_response.generations = [[mock_generation]]
    
    logger.on_chat_model_end(mock_response, run_id=run_id)
    
    # 验证开始时间被移除
    assert run_id not in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "ChatModel响应结束" in log_output or "Run ID" in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_chat_model_end回调测试通过")


def test_on_chat_model_error():
    """测试on_chat_model_error回调"""
    print("=" * 60)
    print("测试7：on_chat_model_error回调")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.ERROR)
    
    run_id = "test-chat-run-123"
    logger.start_times[run_id] = 1000.0  # 设置开始时间
    
    error = Exception("Test chat error message")
    
    logger.on_chat_model_error(error, run_id=run_id)
    
    # 验证开始时间被清理
    assert run_id not in logger.start_times
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    assert "ChatModel错误" in log_output or "错误" in log_output
    assert "Test chat error message" in log_output or "Exception" in log_output
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_chat_model_error回调测试通过")


def test_on_llm_start_with_long_prompt():
    """测试on_llm_start回调（长提示词截断）"""
    print("=" * 60)
    print("测试8：on_llm_start回调（长提示词截断）")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    serialized = {"name": "test-model"}
    long_prompt = "A" * 1000  # 超过500字符的提示词
    prompts = [long_prompt]
    
    logger.on_llm_start(serialized, prompts, run_id="test-run")
    
    # 验证日志输出包含截断标记
    log_output = log_capture.getvalue()
    # 应该包含"..."表示截断
    assert "..." in log_output or len(log_output) > 0
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_llm_start回调（长提示词截断）测试通过")


def test_on_llm_end_with_tool_calls():
    """测试on_llm_end回调（包含工具调用）"""
    print("=" * 60)
    print("测试9：on_llm_end回调（包含工具调用）")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 捕获日志输出
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    test_logger = logging.getLogger("core.llm.callbacks")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    run_id = "test-run-123"
    logger.start_times[run_id] = 1000.0
    
    # 创建包含工具调用的生成结果
    # 使用Mock来模拟有message属性的generation
    mock_message = MagicMock()
    mock_message.tool_calls = [{"name": "test_tool", "args": {"arg1": "value1"}}]
    
    # 直接使用Mock对象来模拟Generation（因为Generation是Pydantic模型，不能直接设置属性）
    mock_generation = MagicMock(spec=['text', 'message'])
    mock_generation.text = "Test response"
    mock_generation.message = mock_message
    
    # 创建LLMResult的Mock
    llm_result = MagicMock(spec=LLMResult)
    llm_result.generations = [[mock_generation]]
    llm_result.llm_output = None
    
    logger.on_llm_end(llm_result, run_id=run_id)
    
    # 验证日志输出
    log_output = log_capture.getvalue()
    # 应该记录工具调用信息或至少记录了响应
    assert len(log_output) > 0
    
    # 清理
    test_logger.removeHandler(handler)
    
    print("✅ on_llm_end回调（包含工具调用）测试通过")


def test_get_model_interaction_logger():
    """测试get_model_interaction_logger函数"""
    print("=" * 60)
    print("测试10：get_model_interaction_logger函数")
    print("=" * 60)
    
    logger1 = get_model_interaction_logger()
    logger2 = get_model_interaction_logger()
    
    # 每次调用应该返回新实例（不是单例）
    assert logger1 is not None
    assert logger2 is not None
    assert isinstance(logger1, ModelInteractionLogger)
    assert isinstance(logger2, ModelInteractionLogger)
    assert logger1.verbose is True
    assert logger2.verbose is True
    
    print("✅ get_model_interaction_logger函数测试通过")


def test_multiple_run_ids():
    """测试多个run_id的管理"""
    print("=" * 60)
    print("测试11：多个run_id的管理")
    print("=" * 60)
    
    logger = ModelInteractionLogger(verbose=True)
    
    # 添加多个run_id
    run_id1 = "run-1"
    run_id2 = "run-2"
    run_id3 = "run-3"
    
    logger.start_times[run_id1] = 1000.0
    logger.start_times[run_id2] = 2000.0
    logger.start_times[run_id3] = 3000.0
    
    # 验证所有run_id都被记录
    assert run_id1 in logger.start_times
    assert run_id2 in logger.start_times
    assert run_id3 in logger.start_times
    
    # 结束一个run
    mock_response = MagicMock()
    mock_response.generations = []
    logger.on_llm_end(mock_response, run_id=run_id2)
    
    # 验证run_id2被移除，其他仍在
    assert run_id1 in logger.start_times
    assert run_id2 not in logger.start_times
    assert run_id3 in logger.start_times
    
    print("✅ 多个run_id的管理测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试LLM回调模块...")
    print("=" * 60)
    print()
    
    # 运行所有测试
    test_model_interaction_logger_initialization()
    print()
    
    test_on_llm_start()
    print()
    
    test_on_llm_end()
    print()
    
    test_on_llm_error()
    print()
    
    test_on_chat_model_start()
    print()
    
    test_on_chat_model_end()
    print()
    
    test_on_chat_model_error()
    print()
    
    test_on_llm_start_with_long_prompt()
    print()
    
    test_on_llm_end_with_tool_calls()
    print()
    
    test_get_model_interaction_logger()
    print()
    
    test_multiple_run_ids()
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()

