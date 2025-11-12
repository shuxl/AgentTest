"""
日志管理模块测试
测试core.logging模块的功能
"""
import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.logging import (
    setup_logging,
    create_formatter,
    create_console_handler,
    create_file_handler
)
from core.config import Settings, get_settings


def test_create_formatter_default():
    """测试日志格式化器创建（默认格式）"""
    print("=" * 60)
    print("测试1：日志格式化器创建（默认格式）")
    print("=" * 60)
    
    formatter = create_formatter()
    
    assert formatter is not None
    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert formatter.datefmt == "%Y-%m-%d %H:%M:%S"
    
    print("✅ 日志格式化器创建（默认格式）测试通过")


def test_create_formatter_custom():
    """测试日志格式化器创建（自定义格式）"""
    print("=" * 60)
    print("测试2：日志格式化器创建（自定义格式）")
    print("=" * 60)
    
    custom_fmt = "%(levelname)s: %(message)s"
    custom_datefmt = "%Y-%m-%d"
    
    formatter = create_formatter(fmt=custom_fmt, datefmt=custom_datefmt)
    
    assert formatter is not None
    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == custom_fmt
    assert formatter.datefmt == custom_datefmt
    
    print("✅ 日志格式化器创建（自定义格式）测试通过")


def test_create_console_handler_default():
    """测试控制台处理器创建（默认配置）"""
    print("=" * 60)
    print("测试3：控制台处理器创建（默认配置）")
    print("=" * 60)
    
    handler = create_console_handler()
    
    assert handler is not None
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.DEBUG
    assert handler.formatter is not None
    assert handler.stream == sys.stdout
    
    print("✅ 控制台处理器创建（默认配置）测试通过")


def test_create_console_handler_custom():
    """测试控制台处理器创建（自定义配置）"""
    print("=" * 60)
    print("测试4：控制台处理器创建（自定义配置）")
    print("=" * 60)
    
    custom_formatter = create_formatter(fmt="%(message)s")
    custom_stream = StringIO()
    
    handler = create_console_handler(
        level=logging.WARNING,
        formatter=custom_formatter,
        stream=custom_stream
    )
    
    assert handler is not None
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.WARNING
    assert handler.formatter == custom_formatter
    assert handler.stream == custom_stream
    
    print("✅ 控制台处理器创建（自定义配置）测试通过")


def test_create_file_handler_default():
    """测试文件处理器创建（默认配置）"""
    print("=" * 60)
    print("测试5：文件处理器创建（默认配置）")
    print("=" * 60)
    
    # 创建临时目录和文件
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test.log")
    
    try:
        handler = create_file_handler(log_file=temp_file)
        
        assert handler is not None
        # ConcurrentRotatingFileHandler 继承自 RotatingFileHandler
        assert isinstance(handler, logging.handlers.RotatingFileHandler) or \
               hasattr(handler, 'baseFilename')
        assert handler.level == logging.DEBUG
        assert handler.formatter is not None
        
        # 验证文件路径（文件可能还未创建，但路径应该正确）
        if hasattr(handler, 'baseFilename'):
            assert handler.baseFilename == temp_file or os.path.abspath(handler.baseFilename) == os.path.abspath(temp_file)
        
        print("✅ 文件处理器创建（默认配置）测试通过")
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_create_file_handler_custom():
    """测试文件处理器创建（自定义配置）"""
    print("=" * 60)
    print("测试6：文件处理器创建（自定义配置）")
    print("=" * 60)
    
    # 创建临时目录和文件
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_custom.log")
    
    try:
        custom_formatter = create_formatter(fmt="%(message)s")
        max_bytes = 1024 * 1024  # 1MB
        backup_count = 5
        
        handler = create_file_handler(
            log_file=temp_file,
            level=logging.ERROR,
            formatter=custom_formatter,
            max_bytes=max_bytes,
            backup_count=backup_count
        )
        
        assert handler is not None
        assert handler.level == logging.ERROR
        assert handler.formatter == custom_formatter
        # 验证文件路径（文件可能还未创建，但路径应该正确）
        if hasattr(handler, 'baseFilename'):
            assert handler.baseFilename == temp_file or os.path.abspath(handler.baseFilename) == os.path.abspath(temp_file)
        
        print("✅ 文件处理器创建（自定义配置）测试通过")
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_console_handler_log_output():
    """测试控制台处理器日志输出"""
    print("=" * 60)
    print("测试7：控制台处理器日志输出")
    print("=" * 60)
    
    # 创建字符串流来捕获日志输出
    log_stream = StringIO()
    handler = create_console_handler(stream=log_stream)
    
    # 创建测试日志记录器
    test_logger = logging.getLogger("test_console")
    test_logger.setLevel(logging.DEBUG)
    test_logger.handlers = []  # 清除现有处理器
    test_logger.addHandler(handler)
    
    # 输出测试日志
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")
    
    # 获取输出内容
    output = log_stream.getvalue()
    
    # 验证输出包含日志消息
    assert "Debug message" in output
    assert "Info message" in output
    assert "Warning message" in output
    assert "Error message" in output
    
    print("✅ 控制台处理器日志输出测试通过")


def test_file_handler_log_output():
    """测试文件处理器日志输出"""
    print("=" * 60)
    print("测试8：文件处理器日志输出")
    print("=" * 60)
    
    # 创建临时目录和文件
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_output.log")
    
    try:
        handler = create_file_handler(log_file=temp_file)
        
        # 创建测试日志记录器
        test_logger = logging.getLogger("test_file")
        test_logger.setLevel(logging.DEBUG)
        test_logger.handlers = []  # 清除现有处理器
        test_logger.addHandler(handler)
        
        # 输出测试日志
        test_logger.debug("Debug message to file")
        test_logger.info("Info message to file")
        test_logger.warning("Warning message to file")
        test_logger.error("Error message to file")
        
        # 确保日志被刷新到文件
        handler.flush()
        
        # 读取文件内容
        content = ""
        # 尝试从handler获取实际文件路径
        actual_file = temp_file
        if hasattr(handler, 'baseFilename'):
            actual_file = handler.baseFilename
        
        if os.path.exists(actual_file):
            with open(actual_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 验证文件内容包含日志消息
        assert "Debug message to file" in content or "debug" in content.lower()
        assert "Info message to file" in content or "info" in content.lower()
        assert "Warning message to file" in content or "warning" in content.lower()
        assert "Error message to file" in content or "error" in content.lower()
        
        print("✅ 文件处理器日志输出测试通过")
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_log_format():
    """测试日志格式"""
    print("=" * 60)
    print("测试9：日志格式")
    print("=" * 60)
    
    # 创建字符串流来捕获日志输出
    log_stream = StringIO()
    formatter = create_formatter()
    handler = create_console_handler(stream=log_stream, formatter=formatter)
    
    # 创建测试日志记录器
    test_logger = logging.getLogger("test_format")
    test_logger.setLevel(logging.DEBUG)
    test_logger.handlers = []  # 清除现有处理器
    test_logger.addHandler(handler)
    
    # 输出测试日志
    test_logger.info("Test message")
    
    # 获取输出内容
    output = log_stream.getvalue()
    
    # 验证日志格式包含必要字段
    assert "test_format" in output  # 日志记录器名称
    assert "INFO" in output  # 日志级别
    assert "Test message" in output  # 日志消息
    # 验证时间戳格式（应该包含日期和时间）
    assert "-" in output  # 格式分隔符
    
    print("✅ 日志格式测试通过")


def test_setup_logging_initialization():
    """测试日志配置初始化"""
    print("=" * 60)
    print("测试10：日志配置初始化")
    print("=" * 60)
    
    # 创建临时目录和文件
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "app.log")
    
    try:
        # 创建测试配置
        settings = Settings()
        # 使用临时文件路径
        settings.log_file = temp_file
        
        # 保存原始根日志记录器状态
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers.copy()
        original_level = root_logger.level
        
        try:
            # 初始化日志配置
            setup_logging(settings)
            
            # 验证根日志记录器已配置
            assert root_logger.level == logging.DEBUG
            
            # 验证已添加处理器
            handlers = root_logger.handlers
            assert len(handlers) >= 2  # 至少应该有控制台和文件处理器
            
            # 验证处理器类型
            has_console_handler = any(
                isinstance(h, logging.StreamHandler) for h in handlers
            )
            has_file_handler = any(
                isinstance(h, logging.handlers.RotatingFileHandler) or 
                hasattr(h, 'baseFilename') for h in handlers
            )
            
            assert has_console_handler, "应该有控制台处理器"
            assert has_file_handler, "应该有文件处理器"
            
            print("✅ 日志配置初始化测试通过")
        finally:
            # 恢复原始状态
            root_logger.handlers = original_handlers
            root_logger.level = original_level
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_setup_logging_with_default_settings():
    """测试日志配置初始化（使用默认配置）"""
    print("=" * 60)
    print("测试11：日志配置初始化（使用默认配置）")
    print("=" * 60)
    
    # 保存原始根日志记录器状态
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level
    
    try:
        # 初始化日志配置（不传递settings，使用默认）
        setup_logging()
        
        # 验证根日志记录器已配置
        assert root_logger.level == logging.DEBUG
        
        # 验证已添加处理器
        handlers = root_logger.handlers
        assert len(handlers) >= 2  # 至少应该有控制台和文件处理器
        
        print("✅ 日志配置初始化（使用默认配置）测试通过")
    finally:
        # 恢复原始状态
        root_logger.handlers = original_handlers
        root_logger.level = original_level


def test_log_level_filtering():
    """测试日志级别过滤"""
    print("=" * 60)
    print("测试12：日志级别过滤")
    print("=" * 60)
    
    # 创建字符串流来捕获日志输出
    log_stream = StringIO()
    handler = create_console_handler(level=logging.WARNING, stream=log_stream)
    
    # 创建测试日志记录器
    test_logger = logging.getLogger("test_level")
    test_logger.setLevel(logging.DEBUG)
    test_logger.handlers = []  # 清除现有处理器
    test_logger.addHandler(handler)
    
    # 输出不同级别的日志
    test_logger.debug("Debug message (should be filtered)")
    test_logger.info("Info message (should be filtered)")
    test_logger.warning("Warning message (should be shown)")
    test_logger.error("Error message (should be shown)")
    
    # 获取输出内容
    output = log_stream.getvalue()
    
    # 验证低级别日志被过滤
    assert "Debug message" not in output
    assert "Info message" not in output
    
    # 验证高级别日志被输出
    assert "Warning message" in output
    assert "Error message" in output
    
    print("✅ 日志级别过滤测试通过")


def test_file_handler_directory_creation():
    """测试文件处理器自动创建目录"""
    print("=" * 60)
    print("测试13：文件处理器自动创建目录")
    print("=" * 60)
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    nested_dir = os.path.join(temp_dir, "nested", "subdir")
    log_file = os.path.join(nested_dir, "test.log")
    
    try:
        # 目录应该不存在
        assert not os.path.exists(nested_dir)
        
        # 创建文件处理器（应该自动创建目录）
        handler = create_file_handler(log_file=log_file)
        
        # 验证目录已被创建
        assert os.path.exists(nested_dir)
        
        # 验证文件路径正确（文件可能还未创建，但路径应该正确）
        if hasattr(handler, 'baseFilename'):
            assert handler.baseFilename == log_file or os.path.abspath(handler.baseFilename) == os.path.abspath(log_file)
        
        print("✅ 文件处理器自动创建目录测试通过")
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试日志管理模块...")
    print("=" * 60)
    print()
    
    # 运行所有测试
    test_create_formatter_default()
    print()
    
    test_create_formatter_custom()
    print()
    
    test_create_console_handler_default()
    print()
    
    test_create_console_handler_custom()
    print()
    
    test_create_file_handler_default()
    print()
    
    test_create_file_handler_custom()
    print()
    
    test_console_handler_log_output()
    print()
    
    test_file_handler_log_output()
    print()
    
    test_log_format()
    print()
    
    test_setup_logging_initialization()
    print()
    
    test_setup_logging_with_default_settings()
    print()
    
    test_log_level_filtering()
    print()
    
    test_file_handler_directory_creation()
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()

