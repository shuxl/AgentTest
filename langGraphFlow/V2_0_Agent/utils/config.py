"""
配置模块（向后兼容层）
此模块已迁移到 core.config.Settings，保留此文件以保持向后兼容
建议新代码使用：from core.config import Settings
"""
import warnings
from core.config import get_settings

# 获取新的配置实例
_settings = get_settings()


class Config:
    """
    统一的配置类（向后兼容层）
    
    注意：此类的实现已迁移到 core.config.Settings
    建议新代码使用：from core.config import Settings, get_settings
    """
    
    # 日志持久化存储
    @property
    def LOG_FILE(self):
        """日志文件路径"""
        return _settings.LOG_FILE
    
    @property
    def MAX_BYTES(self):
        """日志文件最大字节数"""
        return _settings.MAX_BYTES
    
    @property
    def BACKUP_COUNT(self):
        """日志备份文件数量"""
        return _settings.BACKUP_COUNT

    # PostgreSQL数据库配置参数
    @property
    def DB_URI(self):
        """PostgreSQL数据库连接URI"""
        return _settings.DB_URI
    
    @property
    def DB_TIMEZONE(self):
        """数据库时区设置"""
        return _settings.DB_TIMEZONE
    
    @property
    def MIN_SIZE(self):
        """连接池最小连接数"""
        return _settings.MIN_SIZE
    
    @property
    def MAX_SIZE(self):
        """连接池最大连接数"""
        return _settings.MAX_SIZE

    # Redis数据库配置参数
    @property
    def REDIS_HOST(self):
        """Redis服务器地址"""
        return _settings.REDIS_HOST
    
    @property
    def REDIS_PORT(self):
        """Redis服务器端口"""
        return _settings.REDIS_PORT
    
    @property
    def REDIS_DB(self):
        """Redis数据库编号"""
        return _settings.REDIS_DB
    
    @property
    def SESSION_TIMEOUT(self):
        """会话超时时间（秒）"""
        return _settings.SESSION_TIMEOUT
    
    @property
    def TTL(self):
        """Redis键过期时间（秒）"""
        return _settings.TTL

    @property
    def CELERY_BROKER_URL(self):
        """Celery Broker URL"""
        return _settings.CELERY_BROKER_URL
    
    @property
    def TASK_TTL(self):
        """任务过期时间（秒）"""
        return _settings.TASK_TTL

    # LLM配置
    @property
    def LLM_TYPE(self):
        """LLM类型"""
        return _settings.LLM_TYPE
    
    @property
    def LLM_TEMPERATURE(self):
        """LLM温度参数"""
        return _settings.LLM_TEMPERATURE
    
    @property
    def LLM_API_KEY_ENV_NAME(self):
        """LLM API Key环境变量名称"""
        return _settings.LLM_API_KEY_ENV_NAME

    # API服务地址和端口
    @property
    def HOST(self):
        """服务监听地址"""
        return _settings.HOST
    
    @property
    def PORT(self):
        """服务监听端口"""
        return _settings.PORT

    # 路由配置
    @property
    def INTENT_CONFIDENCE_THRESHOLD(self):
        """意图识别置信度阈值"""
        return _settings.INTENT_CONFIDENCE_THRESHOLD
    
    @property
    def MAX_DIALOGUE_ROUNDS(self):
        """最大对话轮数"""
        return _settings.MAX_DIALOGUE_ROUNDS

    # Java微服务配置（预留）
    @property
    def JAVA_SERVICE_BASE_URL(self):
        """Java微服务基础URL"""
        return _settings.JAVA_SERVICE_BASE_URL
    
    @property
    def JAVA_SERVICE_TIMEOUT(self):
        """Java微服务超时时间（秒）"""
        return _settings.JAVA_SERVICE_TIMEOUT
    
    @property
    def JAVA_SERVICE_API_KEY(self):
        """Java微服务API认证密钥"""
        return _settings.JAVA_SERVICE_API_KEY


# 创建全局Config实例（向后兼容）
Config = Config()

# 发出警告，提示使用新模块
warnings.warn(
    "utils.config.Config 已迁移到 core.config.Settings，"
    "建议使用：from core.config import Settings, get_settings",
    DeprecationWarning,
    stacklevel=2
)

