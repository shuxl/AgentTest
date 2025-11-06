import os


class Config:
    """统一的配置类，集中管理所有常量"""
    
    # 日志持久化存储
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logfile", "app.log")
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    MAX_BYTES = 5 * 1024 * 1024
    BACKUP_COUNT = 3

    # PostgreSQL数据库配置参数
    DB_URI = os.getenv("DB_URI", "postgresql://postgres:sxl_pwd_123@localhost:5433/doctor_agent_db?sslmode=disable")
    DB_TIMEZONE = os.getenv("DB_TIMEZONE", "Asia/Shanghai")  # 数据库时区设置
    MIN_SIZE = 5  # 连接池最小连接数
    MAX_SIZE = 10  # 连接池最大连接数

    # Redis数据库配置参数
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 会话超时时间（秒）
    TTL = int(os.getenv("REDIS_TTL", "3600"))  # Redis键过期时间（秒）

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    TASK_TTL = int(os.getenv("TASK_TTL", "3600"))  # 任务过期时间（秒）

    # LLM配置
    # openai:调用gpt模型,qwen:调用阿里通义千问大模型,oneapi:调用oneapi方案支持的模型,ollama:调用本地开源大模型
    LLM_TYPE = os.getenv("LLM_TYPE", "deepseek-chat")
    # LLM温度参数
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
    # LLM API Key的环境变量名称
    LLM_API_KEY_ENV_NAME = os.getenv("LLM_API_KEY_ENV_NAME", "DEEPSEEK_API_KEY")

    # API服务地址和端口
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8001"))

    # 路由配置
    INTENT_CONFIDENCE_THRESHOLD = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.7"))  # 意图识别置信度阈值
    MAX_DIALOGUE_ROUNDS = int(os.getenv("MAX_DIALOGUE_ROUNDS", "100"))  # 最大对话轮数

    # Java微服务配置（预留）
    JAVA_SERVICE_BASE_URL = os.getenv("JAVA_SERVICE_BASE_URL", "http://localhost:8080")
    JAVA_SERVICE_TIMEOUT = int(os.getenv("JAVA_SERVICE_TIMEOUT", "30"))  # 超时时间（秒）
    JAVA_SERVICE_API_KEY = os.getenv("JAVA_SERVICE_API_KEY", "")  # API认证密钥

