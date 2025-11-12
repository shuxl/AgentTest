"""
日志处理器模块
提供日志处理器的创建功能
"""
import logging
import sys
import os
from typing import Optional
from concurrent_log_handler import ConcurrentRotatingFileHandler

from .formatters import create_formatter


def create_console_handler(
    level: int = logging.DEBUG,
    formatter: Optional[logging.Formatter] = None,
    stream=sys.stdout
) -> logging.StreamHandler:
    """
    创建控制台日志处理器
    
    Args:
        level: 日志级别，默认为DEBUG
        formatter: 日志格式化器，如果为None则使用默认格式化器
        stream: 输出流，默认为sys.stdout
    
    Returns:
        logging.StreamHandler: 控制台日志处理器实例
    """
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    
    if formatter is None:
        formatter = create_formatter()
    
    handler.setFormatter(formatter)
    return handler


def create_file_handler(
    log_file: str,
    level: int = logging.DEBUG,
    formatter: Optional[logging.Formatter] = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3
) -> ConcurrentRotatingFileHandler:
    """
    创建文件日志处理器
    
    Args:
        log_file: 日志文件路径
        level: 日志级别，默认为DEBUG
        formatter: 日志格式化器，如果为None则使用默认格式化器
        max_bytes: 日志文件最大字节数，默认为5MB
        backup_count: 备份文件数量，默认为3
    
    Returns:
        ConcurrentRotatingFileHandler: 文件日志处理器实例
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    handler = ConcurrentRotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setLevel(level)
    
    if formatter is None:
        formatter = create_formatter()
    
    handler.setFormatter(formatter)
    return handler

