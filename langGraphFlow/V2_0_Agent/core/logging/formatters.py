"""
日志格式化器模块
提供日志格式化器的创建功能
"""
import logging
from typing import Optional


def create_formatter(
    fmt: Optional[str] = None,
    datefmt: Optional[str] = None
) -> logging.Formatter:
    """
    创建日志格式化器
    
    Args:
        fmt: 日志格式字符串，如果为None则使用默认格式
        datefmt: 日期格式字符串，如果为None则使用默认格式
    
    Returns:
        logging.Formatter: 日志格式化器实例
    """
    if fmt is None:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if datefmt is None:
        datefmt = "%Y-%m-%d %H:%M:%S"
    
    return logging.Formatter(fmt, datefmt=datefmt)

