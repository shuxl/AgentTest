"""
配置验证器
提供配置项验证功能
"""
from typing import Optional


def validate_db_uri(uri: str) -> None:
    """
    验证数据库URI格式
    
    Args:
        uri: 数据库连接URI
        
    Raises:
        ValueError: 如果URI格式无效
    """
    if not uri:
        raise ValueError("数据库URI不能为空")
    if not uri.startswith("postgresql://") and not uri.startswith("postgresql+psycopg://"):
        raise ValueError(f"无效的数据库URI格式: {uri}，必须以postgresql://或postgresql+psycopg://开头")


def validate_redis_config(host: str, port: int) -> None:
    """
    验证Redis配置
    
    Args:
        host: Redis主机地址
        port: Redis端口
        
    Raises:
        ValueError: 如果配置无效
    """
    if not host:
        raise ValueError("Redis主机地址不能为空")
    if not (1 <= port <= 65535):
        raise ValueError(f"Redis端口必须在1-65535之间: {port}")


def validate_port(port: int, name: str = "端口") -> None:
    """
    验证端口号
    
    Args:
        port: 端口号
        name: 端口名称（用于错误提示）
        
    Raises:
        ValueError: 如果端口号无效
    """
    if not (1 <= port <= 65535):
        raise ValueError(f"{name}必须在1-65535之间: {port}")


def validate_temperature(temperature: float) -> None:
    """
    验证LLM温度参数
    
    Args:
        temperature: 温度参数
        
    Raises:
        ValueError: 如果温度参数无效
    """
    if not (0.0 <= temperature <= 2.0):
        raise ValueError(f"LLM温度参数必须在0.0-2.0之间: {temperature}")


def validate_confidence_threshold(threshold: float) -> None:
    """
    验证置信度阈值
    
    Args:
        threshold: 置信度阈值
        
    Raises:
        ValueError: 如果阈值无效
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"置信度阈值必须在0.0-1.0之间: {threshold}")

