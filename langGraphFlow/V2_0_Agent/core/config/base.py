"""
配置基类
提供统一的配置管理接口
"""
from pydantic_settings import BaseSettings
from typing import Optional, Any
from pathlib import Path
import os


class BaseConfig(BaseSettings):
    """配置基类，提供统一的配置管理接口"""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略未定义的配置项
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项名称
            default: 默认值
            
        Returns:
            配置项值，如果不存在则返回默认值
        """
        return getattr(self, key, default)
    
    def validate_all(self) -> None:
        """
        验证所有配置项
        子类可以重写此方法以实现自定义验证逻辑
        """
        pass

