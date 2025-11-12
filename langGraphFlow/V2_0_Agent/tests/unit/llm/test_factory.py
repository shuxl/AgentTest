"""
LLM工厂模块测试
测试core.llm.factory模块的功能
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.llm import LLMFactory, get_llm_factory, get_llm_by_config, InitializationError, APIError
from core.config import Settings


def test_llm_factory_initialization():
    """测试LLMFactory初始化"""
    print("=" * 60)
    print("测试1：LLMFactory初始化")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    assert factory is not None
    assert factory.settings == settings
    assert factory.settings.llm_type is not None
    assert factory.settings.llm_temperature is not None
    
    print("✅ LLMFactory初始化测试通过")


def test_get_api_key_success():
    """测试_get_api_key方法（成功）"""
    print("=" * 60)
    print("测试2：_get_api_key方法（成功）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # 设置测试环境变量
    test_env_key = "TEST_API_KEY"
    test_api_key = "test_api_key_value_12345"
    
    with patch.dict(os.environ, {test_env_key: test_api_key}):
        result = factory._get_api_key(env_key_name=test_env_key)
        assert result == test_api_key
    
    print("✅ _get_api_key方法（成功）测试通过")


def test_get_api_key_from_settings():
    """测试_get_api_key方法（从配置获取环境变量名）"""
    print("=" * 60)
    print("测试3：_get_api_key方法（从配置获取环境变量名）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # 使用配置中的环境变量名
    test_api_key = "test_api_key_from_config"
    
    with patch.dict(os.environ, {settings.llm_api_key_env_name: test_api_key}):
        result = factory._get_api_key()
        assert result == test_api_key
    
    print("✅ _get_api_key方法（从配置获取环境变量名）测试通过")


def test_get_api_key_missing():
    """测试_get_api_key方法（API Key缺失）"""
    print("=" * 60)
    print("测试4：_get_api_key方法（API Key缺失）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # 确保环境变量不存在
    test_env_key = "NON_EXISTENT_API_KEY"
    
    with patch.dict(os.environ, {}, clear=True):
        try:
            factory._get_api_key(env_key_name=test_env_key)
            assert False, "应该抛出InitializationError"
        except InitializationError as e:
            assert test_env_key in str(e)
            print("✅ _get_api_key方法（API Key缺失）测试通过")


def test_get_api_key_empty():
    """测试_get_api_key方法（API Key为空）"""
    print("=" * 60)
    print("测试5：_get_api_key方法（API Key为空）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    test_env_key = "EMPTY_API_KEY"
    
    with patch.dict(os.environ, {test_env_key: ""}):
        try:
            factory._get_api_key(env_key_name=test_env_key)
            assert False, "应该抛出InitializationError"
        except InitializationError as e:
            assert test_env_key in str(e)
            print("✅ _get_api_key方法（API Key为空）测试通过")


def test_create_with_defaults():
    """测试create方法（使用默认配置）"""
    print("=" * 60)
    print("测试6：create方法（使用默认配置）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # Mock init_chat_model
    mock_llm = MagicMock()
    mock_llm.callbacks = []
    
    test_api_key = "test_api_key_12345"
    
    with patch.dict(os.environ, {settings.llm_api_key_env_name: test_api_key}):
        with patch('core.llm.factory.init_chat_model', return_value=mock_llm):
            with patch('core.llm.factory.get_model_interaction_logger', return_value=MagicMock()):
                llm = factory.create()
                
                assert llm is not None
                assert llm == mock_llm
    
    print("✅ create方法（使用默认配置）测试通过")


def test_create_with_custom_params():
    """测试create方法（使用自定义参数）"""
    print("=" * 60)
    print("测试7：create方法（使用自定义参数）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # Mock init_chat_model
    mock_llm = MagicMock()
    mock_llm.callbacks = []
    
    test_api_key = "test_api_key_12345"
    custom_model = "openai:gpt-4"
    custom_temperature = 0.7
    custom_base_url = "https://api.custom.com"
    
    with patch.dict(os.environ, {"CUSTOM_API_KEY": test_api_key}):
        with patch('core.llm.factory.init_chat_model', return_value=mock_llm) as mock_init:
            with patch('core.llm.factory.get_model_interaction_logger', return_value=MagicMock()):
                llm = factory.create(
                    model=custom_model,
                    temperature=custom_temperature,
                    base_url=custom_base_url,
                    api_key=test_api_key
                )
                
                assert llm is not None
                # 验证init_chat_model被正确调用
                mock_init.assert_called_once()
                call_kwargs = mock_init.call_args[1]
                assert call_kwargs['model'] == custom_model
                assert call_kwargs['temperature'] == custom_temperature
                assert call_kwargs['base_url'] == custom_base_url
                assert call_kwargs['api_key'] == test_api_key
    
    print("✅ create方法（使用自定义参数）测试通过")


def test_create_with_callbacks():
    """测试create方法（使用自定义回调）"""
    print("=" * 60)
    print("测试8：create方法（使用自定义回调）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # Mock init_chat_model
    mock_llm = MagicMock()
    mock_llm.callbacks = []
    
    test_api_key = "test_api_key_12345"
    custom_callbacks = [MagicMock(), MagicMock()]
    
    with patch.dict(os.environ, {settings.llm_api_key_env_name: test_api_key}):
        with patch('core.llm.factory.init_chat_model', return_value=mock_llm):
            llm = factory.create(callbacks=custom_callbacks)
            
            assert llm is not None
            # 验证回调被设置
            assert hasattr(llm, 'callbacks')
    
    print("✅ create方法（使用自定义回调）测试通过")


def test_create_initialization_error():
    """测试create方法（初始化错误）"""
    print("=" * 60)
    print("测试9：create方法（初始化错误）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # Mock init_chat_model抛出异常
    with patch.dict(os.environ, {settings.llm_api_key_env_name: "test_key"}):
        with patch('core.llm.factory.init_chat_model', side_effect=Exception("Connection failed")):
            try:
                factory.create()
                assert False, "应该抛出InitializationError"
            except InitializationError as e:
                assert "初始化LLM失败" in str(e)
                print("✅ create方法（初始化错误）测试通过")


def test_create_api_key_error():
    """测试create方法（API Key错误）"""
    print("=" * 60)
    print("测试10：create方法（API Key错误）")
    print("=" * 60)
    
    settings = Settings()
    factory = LLMFactory(settings=settings)
    
    # 确保环境变量不存在
    with patch.dict(os.environ, {}, clear=True):
        try:
            factory.create()
            assert False, "应该抛出InitializationError"
        except InitializationError as e:
            assert "获取API Key失败" in str(e) or settings.llm_api_key_env_name in str(e)
            print("✅ create方法（API Key错误）测试通过")


def test_create_by_config_deepseek():
    """测试create_by_config方法（deepseek-chat）"""
    print("=" * 60)
    print("测试11：create_by_config方法（deepseek-chat）")
    print("=" * 60)
    
    settings = Settings()
    settings.llm_type = "deepseek-chat"
    factory = LLMFactory(settings=settings)
    
    # Mock init_chat_model
    mock_llm = MagicMock()
    mock_llm.callbacks = []
    
    test_api_key = "test_api_key_12345"
    
    with patch.dict(os.environ, {settings.llm_api_key_env_name: test_api_key}):
        with patch('core.llm.factory.init_chat_model', return_value=mock_llm) as mock_init:
            with patch('core.llm.factory.get_model_interaction_logger', return_value=MagicMock()):
                llm = factory.create_by_config()
                
                assert llm is not None
                # 验证init_chat_model被调用，且model参数正确
                mock_init.assert_called_once()
                call_kwargs = mock_init.call_args[1]
                assert call_kwargs['model'] == "openai:deepseek-chat"
    
    print("✅ create_by_config方法（deepseek-chat）测试通过")


def test_create_by_config_invalid_type():
    """测试create_by_config方法（无效的LLM类型）"""
    print("=" * 60)
    print("测试12：create_by_config方法（无效的LLM类型）")
    print("=" * 60)
    
    settings = Settings()
    settings.llm_type = "invalid-llm-type"
    factory = LLMFactory(settings=settings)
    
    try:
        factory.create_by_config()
        assert False, "应该抛出InitializationError"
    except InitializationError as e:
        assert "不支持的LLM类型" in str(e) or "invalid-llm-type" in str(e)
        print("✅ create_by_config方法（无效的LLM类型）测试通过")


def test_create_by_config_empty_type():
    """测试create_by_config方法（空的LLM类型）"""
    print("=" * 60)
    print("测试13：create_by_config方法（空的LLM类型）")
    print("=" * 60)
    
    settings = Settings()
    settings.llm_type = ""
    factory = LLMFactory(settings=settings)
    
    try:
        factory.create_by_config()
        assert False, "应该抛出InitializationError"
    except InitializationError as e:
        assert "LLM_TYPE" in str(e) or "配置错误" in str(e)
        print("✅ create_by_config方法（空的LLM类型）测试通过")


def test_create_by_config_invalid_temperature():
    """测试create_by_config方法（无效的温度参数）"""
    print("=" * 60)
    print("测试14：create_by_config方法（无效的温度参数）")
    print("=" * 60)
    
    settings = Settings()
    settings.llm_type = "deepseek-chat"
    settings.llm_temperature = 3.0  # 超出范围
    
    factory = LLMFactory(settings=settings)
    
    try:
        factory.create_by_config()
        assert False, "应该抛出InitializationError"
    except InitializationError as e:
        assert "LLM_TEMPERATURE" in str(e) or "配置错误" in str(e)
        print("✅ create_by_config方法（无效的温度参数）测试通过")


def test_get_llm_factory_singleton():
    """测试get_llm_factory单例模式"""
    print("=" * 60)
    print("测试15：get_llm_factory单例模式")
    print("=" * 60)
    
    # 清除全局实例（用于测试）
    import core.llm.factory as factory_module
    factory_module._llm_factory = None
    
    factory1 = get_llm_factory()
    factory2 = get_llm_factory()
    
    assert factory1 is factory2
    print("✅ get_llm_factory单例模式测试通过")


def test_get_llm_by_config():
    """测试get_llm_by_config函数"""
    print("=" * 60)
    print("测试16：get_llm_by_config函数")
    print("=" * 60)
    
    # Mock get_llm_factory和create_by_config
    mock_factory = MagicMock()
    mock_llm = MagicMock()
    mock_factory.create_by_config.return_value = mock_llm
    
    with patch('core.llm.factory.get_llm_factory', return_value=mock_factory):
        llm = get_llm_by_config()
        
        assert llm is not None
        assert llm == mock_llm
        mock_factory.create_by_config.assert_called_once()
    
    print("✅ get_llm_by_config函数测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试LLM工厂模块...")
    print("=" * 60)
    print()
    
    # 运行所有测试
    test_llm_factory_initialization()
    print()
    
    test_get_api_key_success()
    print()
    
    test_get_api_key_from_settings()
    print()
    
    test_get_api_key_missing()
    print()
    
    test_get_api_key_empty()
    print()
    
    test_create_with_defaults()
    print()
    
    test_create_with_custom_params()
    print()
    
    test_create_with_callbacks()
    print()
    
    test_create_initialization_error()
    print()
    
    test_create_api_key_error()
    print()
    
    test_create_by_config_deepseek()
    print()
    
    test_create_by_config_invalid_type()
    print()
    
    test_create_by_config_empty_type()
    print()
    
    test_create_by_config_invalid_temperature()
    print()
    
    test_get_llm_factory_singleton()
    print()
    
    test_get_llm_by_config()
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()

