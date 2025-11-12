"""
日志配置模块
提供统一的日志配置功能
"""
import logging
import os
from typing import Optional

from core.config import Settings, get_settings
from .formatters import create_formatter
from .handlers import create_console_handler, create_file_handler


def setup_logging(settings: Optional[Settings] = None):
    """
    设置统一的日志配置
    配置根日志记录器，让所有模块的日志都能输出到控制台和文件
    
    Args:
        settings: 配置实例，如果为None则从get_settings获取
    """
    if settings is None:
        settings = get_settings()
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 清除现有的处理器
    root_logger.handlers = []
    
    # 设置日志级别
    root_logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = create_formatter()
    
    # 1. 添加控制台处理器（输出到stdout）
    console_handler = create_console_handler(level=logging.DEBUG, formatter=formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 添加文件处理器（输出到文件）
    file_handler = create_file_handler(
        log_file=settings.log_file,
        level=logging.DEBUG,
        formatter=formatter,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count
    )
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别（避免过多输出）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # ========== 方案1：增强 OpenAI 客户端日志 ==========
    # 启用 OpenAI 相关日志（用于记录底层 HTTP 请求/响应）
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.DEBUG)
    
    openai_base_client_logger = logging.getLogger("openai._base_client")
    openai_base_client_logger.setLevel(logging.DEBUG)
    
    # 创建专门的模型交互日志文件（用于记录所有模型交互）
    log_dir = os.path.dirname(settings.log_file)
    model_log_file = os.path.join(log_dir, "model_interactions.log")
    model_log_handler = create_file_handler(
        log_file=model_log_file,
        level=logging.DEBUG,
        formatter=formatter,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count
    )
    
    # 为 OpenAI 相关日志添加专门的日志文件处理器
    openai_logger.addHandler(model_log_handler)
    openai_base_client_logger.addHandler(model_log_handler)
    
    # 为模型交互回调日志添加专门的日志文件处理器
    model_callback_logger = logging.getLogger("core.llm.callbacks")
    model_callback_logger.addHandler(model_log_handler)
    
    # 输出初始化信息
    root_logger.info("日志系统初始化完成（控制台+文件）")
    root_logger.info(f"模型交互日志文件: {model_log_file}")

