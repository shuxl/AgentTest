"""
CRUD 基类
提供通用的数据库 CRUD 操作和查询构建器
"""
import logging
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .base import Base

logger = logging.getLogger(__name__)

# 类型变量，用于泛型
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """
    通用 CRUD 基类
    
    提供标准的 CRUD 操作：
    - create: 创建记录
    - get: 根据 ID 获取单个记录
    - get_multi: 获取多个记录（支持过滤、排序、分页）
    - update: 更新记录
    - delete: 删除记录
    
    Example:
        ```python
        from utils.db.crud import CRUDBase
        from utils.db.models import BloodPressureRecord
        
        crud = CRUDBase(BloodPressureRecord)
        
        # 创建记录
        async with get_db_session() as session:
            record = await crud.create(session, {
                "user_id": "user123",
                "systolic": 120,
                "diastolic": 80
            })
        
        # 查询记录
        record = await crud.get(session, id=1)
        records = await crud.get_multi(session, user_id="user123", limit=10)
        ```
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        初始化 CRUD 基类
        
        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model
    
    async def create(
        self,
        session: AsyncSession,
        obj_in: Union[Dict[str, Any], ModelType],
        **kwargs
    ) -> ModelType:
        """
        创建新记录
        
        Args:
            session: 数据库会话
            obj_in: 要创建的对象（字典或模型实例）
            **kwargs: 额外的字段值
        
        Returns:
            ModelType: 创建的记录实例
        
        Raises:
            SQLAlchemyError: 数据库操作失败时抛出
        """
        try:
            if isinstance(obj_in, dict):
                # 合并字典和 kwargs
                data = {**obj_in, **kwargs}
                db_obj = self.model(**data)
            else:
                # 如果已经是模型实例，直接使用
                db_obj = obj_in
                # 更新额外字段
                for key, value in kwargs.items():
                    setattr(db_obj, key, value)
            
            session.add(db_obj)
            await session.flush()  # 刷新以获取 ID
            await session.refresh(db_obj)  # 刷新以获取数据库默认值
            
            logger.info(f"成功创建 {self.model.__name__} 记录: {db_obj}")
            return db_obj
            
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"创建 {self.model.__name__} 记录失败（完整性约束）: {str(e)}")
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"创建 {self.model.__name__} 记录失败: {str(e)}")
            raise
    
    async def get(
        self,
        session: AsyncSession,
        id: Optional[int] = None,
        **filters
    ) -> Optional[ModelType]:
        """
        根据 ID 或过滤条件获取单个记录
        
        Args:
            session: 数据库会话
            id: 记录 ID（如果提供，优先使用）
            **filters: 过滤条件（字段名=值）
        
        Returns:
            Optional[ModelType]: 找到的记录，如果不存在则返回 None
        """
        try:
            query = select(self.model)
            
            if id is not None:
                query = query.where(self.model.id == id)
            else:
                # 使用过滤条件
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        conditions.append(getattr(self.model, key) == value)
                
                if conditions:
                    query = query.where(and_(*conditions))
                else:
                    logger.warning(f"get 方法未提供 id 或过滤条件")
                    return None
            
            result = await session.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if db_obj:
                logger.debug(f"成功获取 {self.model.__name__} 记录: id={id or filters}")
            else:
                logger.debug(f"未找到 {self.model.__name__} 记录: id={id or filters}")
            
            return db_obj
            
        except SQLAlchemyError as e:
            logger.error(f"获取 {self.model.__name__} 记录失败: {str(e)}")
            raise
    
    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        **filters
    ) -> List[ModelType]:
        """
        获取多个记录（支持过滤、排序、分页）
        
        Args:
            session: 数据库会话
            skip: 跳过的记录数（用于分页）
            limit: 返回的最大记录数
            order_by: 排序字段名（默认使用 id）
            order_desc: 是否降序排序
            **filters: 过滤条件（字段名=值）
        
        Returns:
            List[ModelType]: 记录列表
        """
        try:
            query = select(self.model)
            
            # 应用过滤条件
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if value is None:
                        # 处理 None 值（IS NULL）
                        conditions.append(getattr(self.model, key).is_(None))
                    elif isinstance(value, (list, tuple)):
                        # 处理 IN 查询
                        conditions.append(getattr(self.model, key).in_(value))
                    else:
                        conditions.append(getattr(self.model, key) == value)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 排序
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
            else:
                order_column = self.model.id
            
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            db_objs = result.scalars().all()
            
            logger.debug(f"成功获取 {len(db_objs)} 条 {self.model.__name__} 记录")
            return list(db_objs)
            
        except SQLAlchemyError as e:
            logger.error(f"获取多个 {self.model.__name__} 记录失败: {str(e)}")
            raise
    
    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], ModelType],
        **kwargs
    ) -> ModelType:
        """
        更新记录
        
        Args:
            session: 数据库会话
            db_obj: 要更新的记录实例
            obj_in: 更新数据（字典或模型实例）
            **kwargs: 额外的字段值
        
        Returns:
            ModelType: 更新后的记录实例
        """
        try:
            if isinstance(obj_in, dict):
                update_data = {**obj_in, **kwargs}
            else:
                # 如果是模型实例，转换为字典（只包含非 None 字段）
                update_data = {}
                for column in self.model.__table__.columns:
                    value = getattr(obj_in, column.name, None)
                    if value is not None:
                        update_data[column.name] = value
                update_data.update(kwargs)
            
            # 更新字段
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            await session.flush()
            await session.refresh(db_obj)
            
            logger.info(f"成功更新 {self.model.__name__} 记录: id={db_obj.id}")
            return db_obj
            
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"更新 {self.model.__name__} 记录失败: {str(e)}")
            raise
    
    async def delete(
        self,
        session: AsyncSession,
        id: Optional[int] = None,
        db_obj: Optional[ModelType] = None,
        **filters
    ) -> bool:
        """
        删除记录
        
        Args:
            session: 数据库会话
            id: 记录 ID（如果提供，优先使用）
            db_obj: 要删除的记录实例（如果提供，优先使用）
            **filters: 过滤条件（字段名=值）
        
        Returns:
            bool: 是否成功删除
        """
        try:
            if db_obj:
                await session.delete(db_obj)
            elif id is not None:
                query = delete(self.model).where(self.model.id == id)
                await session.execute(query)
            else:
                # 使用过滤条件
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        conditions.append(getattr(self.model, key) == value)
                
                if conditions:
                    query = delete(self.model).where(and_(*conditions))
                    await session.execute(query)
                else:
                    logger.warning(f"delete 方法未提供 id、db_obj 或过滤条件")
                    return False
            
            await session.flush()
            
            logger.info(f"成功删除 {self.model.__name__} 记录: id={id or filters}")
            return True
            
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"删除 {self.model.__name__} 记录失败: {str(e)}")
            raise
    
    async def count(
        self,
        session: AsyncSession,
        **filters
    ) -> int:
        """
        统计记录数量
        
        Args:
            session: 数据库会话
            **filters: 过滤条件（字段名=值）
        
        Returns:
            int: 记录数量
        """
        try:
            query = select(func.count()).select_from(self.model)
            
            # 应用过滤条件
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if value is None:
                        conditions.append(getattr(self.model, key).is_(None))
                    elif isinstance(value, (list, tuple)):
                        conditions.append(getattr(self.model, key).in_(value))
                    else:
                        conditions.append(getattr(self.model, key) == value)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await session.execute(query)
            count = result.scalar()
            
            logger.debug(f"{self.model.__name__} 记录数量: {count}")
            return count or 0
            
        except SQLAlchemyError as e:
            logger.error(f"统计 {self.model.__name__} 记录数量失败: {str(e)}")
            raise


class QueryBuilder:
    """
    查询构建器
    提供更灵活的查询构建方式
    
    Example:
        ```python
        builder = QueryBuilder(BloodPressureRecord)
        query = (
            builder
            .filter(user_id="user123")
            .filter(systolic__gte=120)  # 大于等于
            .order_by("measurement_time", desc=True)
            .limit(10)
            .build()
        )
        ```
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        初始化查询构建器
        
        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model
        self._query = select(model)
        self._conditions = []
        self._order_by = None
        self._order_desc = True
        self._skip = 0
        self._limit = None
    
    def filter(self, **filters) -> "QueryBuilder":
        """
        添加过滤条件
        
        Args:
            **filters: 过滤条件
                - 普通过滤: field=value
                - 大于等于: field__gte=value
                - 小于等于: field__lte=value
                - 大于: field__gt=value
                - 小于: field__lt=value
                - 不等于: field__ne=value
                - IN: field__in=[value1, value2]
                - LIKE: field__like=pattern
        
        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        for key, value in filters.items():
            if "__" in key:
                # 处理操作符
                field_name, operator = key.rsplit("__", 1)
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    
                    if operator == "gte":
                        self._conditions.append(field >= value)
                    elif operator == "lte":
                        self._conditions.append(field <= value)
                    elif operator == "gt":
                        self._conditions.append(field > value)
                    elif operator == "lt":
                        self._conditions.append(field < value)
                    elif operator == "ne":
                        self._conditions.append(field != value)
                    elif operator == "in":
                        self._conditions.append(field.in_(value))
                    elif operator == "like":
                        self._conditions.append(field.like(value))
                    elif operator == "isnull":
                        if value:
                            self._conditions.append(field.is_(None))
                        else:
                            self._conditions.append(field.isnot(None))
            else:
                # 普通等值过滤
                if hasattr(self.model, key):
                    field = getattr(self.model, key)
                    if value is None:
                        self._conditions.append(field.is_(None))
                    elif isinstance(value, (list, tuple)):
                        self._conditions.append(field.in_(value))
                    else:
                        self._conditions.append(field == value)
        
        return self
    
    def order_by(self, field: str, desc: bool = True) -> "QueryBuilder":
        """
        设置排序
        
        Args:
            field: 排序字段名
            desc: 是否降序
        
        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        if hasattr(self.model, field):
            self._order_by = getattr(self.model, field)
            self._order_desc = desc
        return self
    
    def skip(self, n: int) -> "QueryBuilder":
        """
        设置跳过的记录数（用于分页）
        
        Args:
            n: 跳过的记录数
        
        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self._skip = n
        return self
    
    def limit(self, n: int) -> "QueryBuilder":
        """
        设置返回的最大记录数
        
        Args:
            n: 最大记录数
        
        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self._limit = n
        return self
    
    def build(self):
        """
        构建查询对象
        
        Returns:
            Select: SQLAlchemy 查询对象
        """
        query = self._query
        
        # 应用过滤条件
        if self._conditions:
            query = query.where(and_(*self._conditions))
        
        # 应用排序
        if self._order_by:
            if self._order_desc:
                query = query.order_by(self._order_by.desc())
            else:
                query = query.order_by(self._order_by.asc())
        else:
            # 默认按 ID 降序
            query = query.order_by(self.model.id.desc())
        
        # 应用分页
        if self._skip > 0:
            query = query.offset(self._skip)
        if self._limit is not None:
            query = query.limit(self._limit)
        
        return query

