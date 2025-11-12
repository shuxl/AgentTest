"""
配置管理模块测试
测试core.config模块的功能
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config import Settings, get_settings, validate_db_uri, validate_redis_config
from pydantic import ValidationError


def test_default_settings():
    """测试默认配置"""
    settings = Settings()
    assert settings.port == 8001
    assert settings.host == "0.0.0.0"
    assert settings.db_min_size == 5
    assert settings.db_max_size == 10
    print("✅ 默认配置测试通过")


def test_backward_compatibility():
    """测试向后兼容属性"""
    settings = Settings()
    # 测试所有向后兼容属性
    assert settings.LOG_FILE == settings.log_file
    assert settings.MAX_BYTES == settings.log_max_bytes
    assert settings.BACKUP_COUNT == settings.log_backup_count
    assert settings.DB_URI == settings.db_uri
    assert settings.DB_TIMEZONE == settings.db_timezone
    assert settings.MIN_SIZE == settings.db_min_size
    assert settings.MAX_SIZE == settings.db_max_size
    assert settings.REDIS_HOST == settings.redis_host
    assert settings.REDIS_PORT == settings.redis_port
    assert settings.REDIS_DB == settings.redis_db
    assert settings.TTL == settings.redis_ttl
    assert settings.SESSION_TIMEOUT == settings.session_timeout
    assert settings.LLM_TYPE == settings.llm_type
    assert settings.LLM_TEMPERATURE == settings.llm_temperature
    assert settings.LLM_API_KEY_ENV_NAME == settings.llm_api_key_env_name
    assert settings.HOST == settings.host
    assert settings.PORT == settings.port
    assert settings.INTENT_CONFIDENCE_THRESHOLD == settings.intent_confidence_threshold
    assert settings.MAX_DIALOGUE_ROUNDS == settings.max_dialogue_rounds
    print("✅ 向后兼容属性测试通过")


def test_get_settings_singleton():
    """测试get_settings单例模式"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
    print("✅ 单例模式测试通过")


def test_port_validation():
    """测试端口验证"""
    # 有效端口
    settings = Settings(port=8080)
    assert settings.port == 8080
    
    # 无效端口（应该被Pydantic验证）
    try:
        Settings(port=70000)
        assert False, "应该抛出ValidationError"
    except ValidationError:
        print("✅ 端口验证测试通过")


def test_validate_db_uri_valid():
    """测试有效的数据库URI"""
    validate_db_uri("postgresql://user:pass@localhost:5432/dbname")
    validate_db_uri("postgresql+psycopg://user:pass@localhost:5432/dbname")
    print("✅ 数据库URI验证（有效）测试通过")


def test_validate_db_uri_invalid():
    """测试无效的数据库URI"""
    try:
        validate_db_uri("")
        assert False, "应该抛出ValueError"
    except ValueError:
        pass
    
    try:
        validate_db_uri("mysql://user:pass@localhost:3306/dbname")
        assert False, "应该抛出ValueError"
    except ValueError:
        pass
    print("✅ 数据库URI验证（无效）测试通过")


def test_validate_redis_config_valid():
    """测试有效的Redis配置"""
    validate_redis_config("localhost", 6379)
    validate_redis_config("127.0.0.1", 6380)
    print("✅ Redis配置验证（有效）测试通过")


def test_validate_redis_config_invalid():
    """测试无效的Redis配置"""
    try:
        validate_redis_config("", 6379)
        assert False, "应该抛出ValueError"
    except ValueError:
        pass
    
    try:
        validate_redis_config("localhost", 0)
        assert False, "应该抛出ValueError"
    except ValueError:
        pass
    
    try:
        validate_redis_config("localhost", 70000)
        assert False, "应该抛出ValueError"
    except ValueError:
        pass
    print("✅ Redis配置验证（无效）测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试配置管理模块...")
    print("=" * 60)
    
    test_default_settings()
    test_backward_compatibility()
    test_get_settings_singleton()
    test_port_validation()
    test_validate_db_uri_valid()
    test_validate_db_uri_invalid()
    test_validate_redis_config_valid()
    test_validate_redis_config_invalid()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

