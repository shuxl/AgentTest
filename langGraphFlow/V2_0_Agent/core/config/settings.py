"""
项目配置类
从原config.py重构，使用Pydantic进行类型检查和验证
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from .base import BaseConfig
from .validators import (
    validate_db_uri,
    validate_redis_config,
    validate_port,
    validate_temperature,
    validate_confidence_threshold,
)


class Settings(BaseConfig):
    """项目配置类"""
    
    # 日志配置
    log_file: str = Field(
        default="logfile/app.log",
        description="日志文件路径"
    )
    log_max_bytes: int = Field(
        default=5 * 1024 * 1024,
        description="日志文件最大字节数"
    )
    log_backup_count: int = Field(
        default=3,
        ge=1,
        description="日志备份文件数量"
    )
    
    # PostgreSQL数据库配置参数
    db_uri: str = Field(
        default="postgresql://postgres:sxl_pwd_123@localhost:5433/doctor_agent_db?sslmode=disable",
        description="PostgreSQL数据库连接URI"
    )
    db_timezone: str = Field(
        default="Asia/Shanghai",
        description="数据库时区设置"
    )
    db_min_size: int = Field(
        default=5,
        ge=1,
        le=100,
        description="连接池最小连接数"
    )
    db_max_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="连接池最大连接数"
    )
    
    # Redis数据库配置参数
    redis_host: str = Field(
        default="localhost",
        description="Redis服务器地址"
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis服务器端口"
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis数据库编号"
    )
    redis_ttl: int = Field(
        default=3600,
        ge=1,
        description="Redis键过期时间（秒）"
    )
    session_timeout: int = Field(
        default=3600,
        ge=1,
        description="会话超时时间（秒）"
    )
    
    # Celery配置（可选）
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery Broker URL"
    )
    task_ttl: int = Field(
        default=3600,
        ge=1,
        description="任务过期时间（秒）"
    )
    
    # LLM配置
    llm_type: str = Field(
        default="deepseek-chat",
        description="LLM类型（openai/qwen/oneapi/ollama/deepseek-chat）"
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM温度参数"
    )
    llm_api_key_env_name: str = Field(
        default="DEEPSEEK_API_KEY",
        description="LLM API Key环境变量名称"
    )
    
    # API服务地址和端口
    host: str = Field(
        default="0.0.0.0",
        description="服务监听地址"
    )
    port: int = Field(
        default=8001,
        ge=1,
        le=65535,
        description="服务监听端口"
    )
    
    # 路由配置
    intent_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="意图识别置信度阈值"
    )
    max_dialogue_rounds: int = Field(
        default=100,
        ge=1,
        description="最大对话轮数"
    )
    
    # Java微服务配置（预留）
    java_service_base_url: str = Field(
        default="http://localhost:8080",
        description="Java微服务基础URL"
    )
    java_service_timeout: int = Field(
        default=30,
        ge=1,
        description="Java微服务超时时间（秒）"
    )
    java_service_api_key: str = Field(
        default="",
        description="Java微服务API认证密钥"
    )
    
    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: str) -> str:
        """验证日志文件路径，确保目录存在"""
        log_path = Path(v)
        log_dir = log_path.parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("db_uri")
    @classmethod
    def validate_db_uri(cls, v: str) -> str:
        """验证数据库URI"""
        validate_db_uri(v)
        return v
    
    @field_validator("redis_port", "port", "java_service_timeout")
    @classmethod
    def validate_ports(cls, v: int) -> int:
        """验证端口号"""
        validate_port(v)
        return v
    
    @field_validator("llm_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """验证LLM温度参数"""
        validate_temperature(v)
        return v
    
    @field_validator("intent_confidence_threshold")
    @classmethod
    def validate_confidence_threshold(cls, v: float) -> float:
        """验证置信度阈值"""
        validate_confidence_threshold(v)
        return v
    
    def model_post_init(self, __context) -> None:
        """模型初始化后验证"""
        # 验证Redis配置
        validate_redis_config(self.redis_host, self.redis_port)
    
    # 为了向后兼容，提供属性访问方式（兼容原Config类的使用方式）
    @property
    def LOG_FILE(self) -> str:
        """向后兼容：日志文件路径"""
        return self.log_file
    
    @property
    def MAX_BYTES(self) -> int:
        """向后兼容：日志文件最大字节数"""
        return self.log_max_bytes
    
    @property
    def BACKUP_COUNT(self) -> int:
        """向后兼容：日志备份文件数量"""
        return self.log_backup_count
    
    @property
    def DB_URI(self) -> str:
        """向后兼容：数据库URI"""
        return self.db_uri
    
    @property
    def DB_TIMEZONE(self) -> str:
        """向后兼容：数据库时区"""
        return self.db_timezone
    
    @property
    def MIN_SIZE(self) -> int:
        """向后兼容：连接池最小连接数"""
        return self.db_min_size
    
    @property
    def MAX_SIZE(self) -> int:
        """向后兼容：连接池最大连接数"""
        return self.db_max_size
    
    @property
    def REDIS_HOST(self) -> str:
        """向后兼容：Redis主机地址"""
        return self.redis_host
    
    @property
    def REDIS_PORT(self) -> int:
        """向后兼容：Redis端口"""
        return self.redis_port
    
    @property
    def REDIS_DB(self) -> int:
        """向后兼容：Redis数据库编号"""
        return self.redis_db
    
    @property
    def TTL(self) -> int:
        """向后兼容：Redis键过期时间"""
        return self.redis_ttl
    
    @property
    def SESSION_TIMEOUT(self) -> int:
        """向后兼容：会话超时时间"""
        return self.session_timeout
    
    @property
    def CELERY_BROKER_URL(self) -> str:
        """向后兼容：Celery Broker URL"""
        return self.celery_broker_url
    
    @property
    def TASK_TTL(self) -> int:
        """向后兼容：任务过期时间"""
        return self.task_ttl
    
    @property
    def LLM_TYPE(self) -> str:
        """向后兼容：LLM类型"""
        return self.llm_type
    
    @property
    def LLM_TEMPERATURE(self) -> float:
        """向后兼容：LLM温度参数"""
        return self.llm_temperature
    
    @property
    def LLM_API_KEY_ENV_NAME(self) -> str:
        """向后兼容：LLM API Key环境变量名称"""
        return self.llm_api_key_env_name
    
    @property
    def HOST(self) -> str:
        """向后兼容：服务监听地址"""
        return self.host
    
    @property
    def PORT(self) -> int:
        """向后兼容：服务监听端口"""
        return self.port
    
    @property
    def INTENT_CONFIDENCE_THRESHOLD(self) -> float:
        """向后兼容：意图识别置信度阈值"""
        return self.intent_confidence_threshold
    
    @property
    def MAX_DIALOGUE_ROUNDS(self) -> int:
        """向后兼容：最大对话轮数"""
        return self.max_dialogue_rounds
    
    @property
    def JAVA_SERVICE_BASE_URL(self) -> str:
        """向后兼容：Java微服务基础URL"""
        return self.java_service_base_url
    
    @property
    def JAVA_SERVICE_TIMEOUT(self) -> int:
        """向后兼容：Java微服务超时时间"""
        return self.java_service_timeout
    
    @property
    def JAVA_SERVICE_API_KEY(self) -> str:
        """向后兼容：Java微服务API认证密钥"""
        return self.java_service_api_key


# 全局配置实例（单例模式）
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        Settings: 配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

