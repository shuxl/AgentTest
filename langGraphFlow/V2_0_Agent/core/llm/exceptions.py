"""
LLM异常类定义
提供LLM相关的自定义异常
"""


class LLMError(Exception):
    """LLM基础异常类"""
    
    def __init__(self, message: str, original_error: Exception = None):
        """
        初始化LLM异常
        
        Args:
            message: 错误消息
            original_error: 原始异常（可选）
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error
    
    def __str__(self):
        if self.original_error:
            return f"{self.message} (原始错误: {str(self.original_error)})"
        return self.message


class InitializationError(LLMError):
    """初始化错误异常"""
    pass


class APIError(LLMError):
    """API错误异常"""
    pass

