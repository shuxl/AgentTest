"""
数据库异常类定义
提供数据库相关的自定义异常
"""


class DatabaseError(Exception):
    """数据库基础异常类"""
    
    def __init__(self, message: str, original_error: Exception = None):
        """
        初始化数据库异常
        
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


class ConnectionPoolError(DatabaseError):
    """连接池错误异常"""
    pass


class QueryError(DatabaseError):
    """查询错误异常"""
    pass

