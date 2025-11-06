"""
统一的日志配置模块
配置根日志记录器，让所有模块的日志都能输出到控制台和文件
"""
import logging
import sys
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from .config import Config


def setup_logging():
    """
    设置统一的日志配置
    配置根日志记录器，让所有模块的日志都能输出到控制台和文件
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 清除现有的处理器
    root_logger.handlers = []
    
    # 设置日志级别
    root_logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 1. 添加控制台处理器（输出到stdout）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 添加文件处理器（输出到文件）
    log_dir = os.path.dirname(Config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = ConcurrentRotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=Config.MAX_BYTES,
        backupCount=Config.BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别（避免过多输出）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # 输出初始化信息
    root_logger.info("日志系统初始化完成（控制台+文件）")

