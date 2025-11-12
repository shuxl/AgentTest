"""
数据库健康检查器
提供数据库连接池的健康检查功能
"""
import logging
from typing import Dict, Any, Optional
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import AsyncEngine

from .exceptions import ConnectionPoolError

logger = logging.getLogger(__name__)


class HealthChecker:
    """数据库健康检查器"""
    
    def __init__(self, pool: Optional[AsyncConnectionPool] = None, engine: Optional[AsyncEngine] = None):
        """
        初始化健康检查器
        
        Args:
            pool: LangGraph连接池实例（可选）
            engine: SQLAlchemy引擎实例（可选）
        """
        self.pool = pool
        self.engine = engine
    
    async def check(self) -> Dict[str, Any]:
        """
        执行健康检查
        
        Returns:
            dict: 包含健康检查结果的字典
            {
                "status": "ok" | "degraded" | "error",
                "langgraph_pool": {...},
                "sqlalchemy_engine": {...},
                "errors": [...]
            }
        """
        results = {
            "status": "ok",
            "langgraph_pool": None,
            "sqlalchemy_engine": None,
            "errors": []
        }
        
        # 检查LangGraph连接池
        pool_result = await self._check_langgraph_pool()
        results["langgraph_pool"] = pool_result
        if pool_result["status"] != "ok":
            results["errors"].append(f"LangGraph连接池: {pool_result.get('error', '未知错误')}")
        
        # 检查SQLAlchemy引擎
        engine_result = await self._check_sqlalchemy_engine()
        results["sqlalchemy_engine"] = engine_result
        if engine_result["status"] != "ok":
            results["errors"].append(f"SQLAlchemy引擎: {engine_result.get('error', '未知错误')}")
        
        # 确定整体状态
        if results["langgraph_pool"]["status"] == "error" or results["sqlalchemy_engine"]["status"] == "error":
            results["status"] = "error"
        elif results["langgraph_pool"]["status"] != "ok" or results["sqlalchemy_engine"]["status"] != "ok":
            results["status"] = "degraded"
        
        return results
    
    async def _check_langgraph_pool(self) -> Dict[str, Any]:
        """
        检查LangGraph连接池
        
        Returns:
            dict: 连接池检查结果
        """
        if self.pool is None:
            return {
                "status": "error",
                "error": "连接池未初始化"
            }
        
        try:
            # 尝试从连接池获取连接（不实际使用，只测试连接可用性）
            async with self.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    if result and result[0] == 1:
                        return {
                            "status": "ok",
                            "message": "连接池正常"
                        }
                    else:
                        return {
                            "status": "error",
                            "error": "连接池查询返回异常结果"
                        }
        except Exception as e:
            logger.error(f"LangGraph连接池健康检查失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_sqlalchemy_engine(self) -> Dict[str, Any]:
        """
        检查SQLAlchemy引擎
        
        Returns:
            dict: 引擎检查结果
        """
        if self.engine is None:
            return {
                "status": "error",
                "error": "引擎未初始化"
            }
        
        try:
            # 尝试执行简单查询
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                row = result.fetchone()
                if row and row[0] == 1:
                    return {
                        "status": "ok",
                        "message": "引擎正常"
                    }
                else:
                    return {
                        "status": "error",
                        "error": "引擎查询返回异常结果"
                    }
        except Exception as e:
            logger.error(f"SQLAlchemy引擎健康检查失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

