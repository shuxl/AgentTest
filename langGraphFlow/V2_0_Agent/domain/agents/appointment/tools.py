"""
复诊管理工具实现（使用 SQLAlchemy ORM）
包含appointment_booking、query_appointment、update_appointment工具
使用PostgreSQL数据库表appointments存储

注意：
- 已重构为使用 SQLAlchemy ORM，不再直接使用 psycopg
- pool 参数保留以保持接口兼容性，但内部不再使用
- 所有数据库操作通过 SQLAlchemy 的 CRUDBase 进行
"""
import logging
from typing import Optional
from langchain_core.tools import tool
from datetime import datetime
from psycopg_pool import AsyncConnectionPool  # 保留以保持接口兼容性
from langgraph.store.postgres import AsyncPostgresStore

# SQLAlchemy 相关导入
from domain.models import get_async_session, Appointment, CRUDBase

logger = logging.getLogger(__name__)

# 创建 CRUD 实例
crud_appointment = CRUDBase(Appointment)


async def parse_datetime_with_llm(date_str: Optional[str], llm=None) -> tuple[str, str, str]:
    """
    使用LLM解析日期时间字符串，支持相对时间（如"本周一"、"明天"等）
    复用血压记录工具中的时间解析逻辑
    
    Args:
        date_str: 日期时间字符串（支持多种格式，包括相对时间）
        llm: LLM实例（可选），如果为None则自动获取
    
    Returns:
        (timestamp, date, original_description): ISO格式的时间戳、日期字符串和原始描述
    """
    from langchain_core.prompts import ChatPromptTemplate
    from core.llm import get_llm_by_config
    import re
    
    if date_str is None:
        now = datetime.now()
        return now.isoformat(), now.strftime("%Y-%m-%d"), ""
    
    original_description = date_str
    
    # 首先尝试标准格式解析（快速路径）
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
            # 标准日期格式 YYYY-MM-DD
            if len(date_str) == 10:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            elif 'T' in date_str or ' ' in date_str:
                # 带时间的格式
                date_str_clean = date_str.replace(' ', 'T').split('T')[0]
                time_part = date_str.replace(' ', 'T').split('T')[1] if 'T' in date_str.replace(' ', 'T') else None
                dt = datetime.strptime(date_str_clean, "%Y-%m-%d")
                if time_part:
                    try:
                        if ':' in time_part:
                            time_parts = time_part.split(':')
                            dt = dt.replace(hour=int(time_parts[0]), minute=int(time_parts[1]) if len(time_parts) > 1 else 0)
                    except:
                        pass
            else:
                dt = datetime.fromisoformat(date_str.replace(' ', 'T'))
            return dt.isoformat(), dt.strftime("%Y-%m-%d"), original_description
        
        # 尝试其他常见格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat(), dt.strftime("%Y-%m-%d"), original_description
            except ValueError:
                continue
        
    except Exception as e:
        logger.debug(f"标准格式解析失败: {e}")
    
    # 如果标准格式解析失败，且包含相对时间关键词，使用LLM解析
    relative_time_keywords = ["今天", "昨天", "明天", "本周", "上周", "下周", "周一", "周二", "周三", "周四", "周五", "周六", "周日", 
                              "上午", "下午", "晚上", "早上", "中午", "凌晨"]
    
    if any(keyword in date_str for keyword in relative_time_keywords):
        try:
            # 使用LLM解析相对时间
            if llm is None:
                llm = get_llm_by_config()
            
            current_time = datetime.now()
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个时间解析专家。根据当前日期时间，将用户提供的相对时间描述转换为ISO格式的日期时间字符串。

当前日期时间：{current_datetime}
当前日期：{current_date}
今天是：{current_weekday}

规则：
1. 如果用户说"今天"，使用当前日期
2. 如果用户说"昨天"，使用当前日期减1天
3. 如果用户说"明天"，使用当前日期加1天
4. 如果用户说"本周一"，计算本周一的日期（当前日期所在的周一的日期）
5. 如果用户说"上周一"，计算上周一的日期
6. 时间部分：如果用户提到"上午"、"早上"，默认8:00；"下午"默认14:00；"晚上"默认20:00；"中午"默认12:00
7. 如果用户提供了具体时间（如"8点"），使用该时间

请只返回ISO格式的日期时间字符串（YYYY-MM-DDTHH:MM:SS），不要包含任何其他文字。"""),
                ("human", "用户描述的时间：{user_time}")
            ])
            
            current_datetime_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            current_date_str = current_time.strftime("%Y-%m-%d")
            current_weekday_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_time.weekday()]
            
            chain = prompt | llm
            response = chain.invoke({
                "current_datetime": current_datetime_str,
                "current_date": current_date_str,
                "current_weekday": current_weekday_str,
                "user_time": date_str
            })
            
            llm_response = response.content if hasattr(response, 'content') else str(response)
            # 清理LLM响应，提取日期时间
            llm_response = llm_response.strip()
            # 移除可能的引号
            llm_response = llm_response.strip('"').strip("'")
            
            # 解析LLM返回的日期时间
            try:
                if 'T' in llm_response:
                    dt = datetime.fromisoformat(llm_response)
                elif ' ' in llm_response:
                    dt = datetime.strptime(llm_response, "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.strptime(llm_response, "%Y-%m-%d")
                
                logger.info(f"LLM解析相对时间成功: '{date_str}' -> '{dt.isoformat()}'")
                return dt.isoformat(), dt.strftime("%Y-%m-%d"), original_description
            except ValueError as e:
                logger.warning(f"LLM返回的时间格式无法解析: {llm_response}, 错误: {e}")
        except Exception as e:
            logger.warning(f"LLM解析相对时间失败: {date_str}, 错误: {e}")
    
    # 如果所有解析都失败，使用当前时间
    logger.warning(f"日期解析失败: {date_str}，使用当前时间")
    now = datetime.now()
    return now.isoformat(), now.strftime("%Y-%m-%d"), original_description


def validate_appointment_date(appointment_date: datetime) -> tuple[bool, str]:
    """
    验证预约日期时间
    
    Args:
        appointment_date: 预约日期时间
    
    Returns:
        (is_valid, message): 验证结果和消息
    """
    now = datetime.now()
    
    # 预约时间不能是过去时间
    if appointment_date < now:
        return False, f"预约时间 {appointment_date.strftime('%Y-%m-%d %H:%M:%S')} 不能是过去时间。请选择未来的时间。"
    
    return True, ""


def create_appointment_tools(pool: AsyncConnectionPool, user_id: str, store: Optional[AsyncPostgresStore] = None):
    """
    创建复诊管理相关的工具（使用 SQLAlchemy ORM）
    
    Args:
        pool: PostgreSQL数据库连接池实例（保留以保持接口兼容性，实际使用 SQLAlchemy）
        user_id: 用户ID
        store: PostgreSQL Store实例（可选），用于查询用户设置信息（长期记忆）
    
    Returns:
        List[BaseTool]: 工具列表
    """
    
    @tool("appointment_booking", description="创建复诊预约。appointment_date参数支持多种格式，如'今天'、'明天'、'本周一'、'2024-01-15 14:30'等，工具会自动解析。")
    async def appointment_booking(
        department: str,
        appointment_date: str,
        doctor_id: Optional[str] = None,
        doctor_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        创建复诊预约（使用 SQLAlchemy ORM）
        
        Args:
            department: 科室名称
            appointment_date: 预约日期时间（支持多种格式，如"明天下午2点"、"2024-01-15 14:30"等）
            doctor_id: 医生ID（可选）
            doctor_name: 医生姓名（可选）
            notes: 备注信息（可选）
        
        Returns:
            str: 预约结果消息
        """
        logger.info(f"[appointment_booking] 工具被调用，参数: department={department}, appointment_date={appointment_date}, "
                   f"doctor_id={doctor_id}, doctor_name={doctor_name}, notes={notes}, user_id={user_id}")
        try:
            # 解析日期时间（使用LLM支持相对时间解析）
            logger.info(f"[appointment_booking] 开始解析日期时间: {appointment_date}")
            # 先尝试不使用LLM解析（快速路径），如果失败再使用LLM
            timestamp, date, _ = await parse_datetime_with_llm(appointment_date, llm=None)
            logger.info(f"[appointment_booking] 日期时间解析结果: timestamp={timestamp}, date={date}")
            
            # 将ISO格式的时间戳转换为datetime对象
            try:
                if 'Z' in timestamp:
                    appointment_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    appointment_datetime = datetime.fromisoformat(timestamp)
                logger.info(f"[appointment_booking] 转换后的datetime对象: {appointment_datetime}")
            except ValueError as ve:
                # 如果解析失败，使用当前时间
                logger.warning(f"[appointment_booking] 时间解析失败: {ve}，使用当前时间")
                appointment_datetime = datetime.now()
            
            # 验证预约时间
            is_valid, validation_msg = validate_appointment_date(appointment_datetime)
            if not is_valid:
                logger.warning(f"[appointment_booking] 预约时间验证失败: {validation_msg}")
                return validation_msg
            
            logger.info(f"[appointment_booking] 开始数据库插入操作")
            # 使用 SQLAlchemy ORM 创建记录
            async_session_maker = get_async_session()
            async with async_session_maker() as session:
                try:
                    db_obj = await crud_appointment.create(
                        session,
                        {
                            "user_id": user_id,
                            "department": department,
                            "doctor_id": doctor_id,
                            "doctor_name": doctor_name,
                            "appointment_date": appointment_datetime,
                            "status": "pending",
                            "notes": notes or ""
                        }
                    )
                    await session.commit()
                    appointment_id = db_obj.id
                except Exception as e:
                    await session.rollback()
                    raise
            
            logger.info(f"[appointment_booking] 成功为用户 {user_id} 创建预约: ID={appointment_id}, "
                       f"department={department}, appointment_date={appointment_datetime}")
            
            date_str = appointment_datetime.strftime('%Y-%m-%d')
            time_str = appointment_datetime.strftime('%Y-%m-%d %H:%M:%S')
            doctor_info = f"，医生：{doctor_name or doctor_id}" if (doctor_name or doctor_id) else ""
            
            return f"预约成功！预约编号：{appointment_id}，科室：{department}{doctor_info}，预约时间：{time_str}。"
            
        except Exception as e:
            logger.error(f"[appointment_booking] 创建预约失败: {str(e)}")
            import traceback
            logger.error(f"[appointment_booking] 详细错误: {traceback.format_exc()}")
            return f"创建预约时发生错误: {str(e)}"
    
    @tool("query_appointment", description="查询用户的复诊预约记录，支持按状态和时间范围过滤")
    async def query_appointment(
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """
        查询用户的复诊预约记录（使用 SQLAlchemy ORM）
        
        Args:
            status: 预约状态（pending/completed/cancelled），可选
            start_date: 开始日期（ISO格式），可选
            end_date: 结束日期（ISO格式），可选
            limit: 返回记录数量限制，默认10
        
        Returns:
            str: 查询结果，格式化的预约记录列表
        """
        try:
            # 验证状态参数
            if status and status not in ['pending', 'completed', 'cancelled']:
                return f"无效的状态值：{status}。有效状态：pending（待处理）、completed（已完成）、cancelled（已取消）。"
            
            # 使用 SQLAlchemy ORM 查询记录
            async_session_maker = get_async_session()
            async with async_session_maker() as session:
                from sqlalchemy import select, func
                query = select(Appointment).where(Appointment.user_id == user_id)
                
                # 添加状态过滤条件
                if status:
                    query = query.where(Appointment.status == status)
                
                # 添加时间过滤条件
                if start_date:
                    query = query.where(func.date(Appointment.appointment_date) >= start_date)
                if end_date:
                    query = query.where(func.date(Appointment.appointment_date) <= end_date)
                
                # 排序和限制
                query = query.order_by(Appointment.appointment_date.desc()).limit(limit)
                
                result = await session.execute(query)
                rows = result.scalars().all()
            
            if not rows:
                status_msg = f"状态为 {status} 的" if status else ""
                date_msg = ""
                if start_date or end_date:
                    date_msg = f"，时间范围：{start_date or '不限'} 至 {end_date or '不限'}"
                return f"未找到{status_msg}预约记录{date_msg}。"
            
            # 格式化返回结果
            status_map = {
                'pending': '待处理',
                'completed': '已完成',
                'cancelled': '已取消'
            }
            
            result_lines = [f"找到 {len(rows)} 条预约记录：\n"]
            for idx, row in enumerate(rows, 1):
                appointment_id = row.id
                department = row.department
                doctor_id = row.doctor_id or ""
                doctor_name = row.doctor_name or ""
                appointment_date = row.appointment_date
                status = row.status
                notes = row.notes or ""
                
                date_str = appointment_date.strftime('%Y-%m-%d')
                time_str = appointment_date.strftime('%Y-%m-%d %H:%M:%S')
                
                doctor_info = f"，医生：{doctor_name or doctor_id}" if (doctor_name or doctor_id) else ""
                notes_str = f"，备注：{notes}" if notes else ""
                status_str = status_map.get(status, status)
                
                result_lines.append(f"{idx}. 预约编号：{appointment_id}，科室：{department}{doctor_info}，预约时间：{time_str}，状态：{status_str}{notes_str}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"查询预约记录失败: {str(e)}")
            return f"查询预约记录时发生错误: {str(e)}"
    
    @tool("update_appointment", description="更新已存在的复诊预约信息")
    async def update_appointment(
        appointment_id: str,
        department: Optional[str] = None,
        doctor_id: Optional[str] = None,
        doctor_name: Optional[str] = None,
        appointment_date: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        更新已存在的复诊预约信息（使用 SQLAlchemy ORM）
        
        Args:
            appointment_id: 预约ID
            department: 科室名称（可选）
            doctor_id: 医生ID（可选）
            doctor_name: 医生姓名（可选）
            appointment_date: 预约日期时间（可选）
            status: 预约状态（pending/completed/cancelled），可选
            notes: 备注信息（可选）
        
        Returns:
            str: 更新结果消息
        """
        try:
            # 验证状态参数
            if status and status not in ['pending', 'completed', 'cancelled']:
                return f"无效的状态值：{status}。有效状态：pending（待处理）、completed（已完成）、cancelled（已取消）。"
            
            # 解析预约ID
            appointment_id_int = int(appointment_id) if appointment_id.isdigit() else None
            if appointment_id_int is None:
                return f"无效的预约ID: {appointment_id}"
            
            # 使用 SQLAlchemy ORM 查询和更新记录
            async_session_maker = get_async_session()
            async with async_session_maker() as session:
                try:
                    # 查询记录
                    db_obj = await crud_appointment.get(session, id=appointment_id_int, user_id=user_id)
                    
                    if not db_obj:
                        return f"未找到ID为 {appointment_id} 的预约记录。"
                    
                    # 准备更新数据
                    update_data = {}
                    
                    if department is not None:
                        update_data["department"] = department
                    if doctor_id is not None:
                        update_data["doctor_id"] = doctor_id
                    if doctor_name is not None:
                        update_data["doctor_name"] = doctor_name
                    if status is not None:
                        update_data["status"] = status
                    if notes is not None:
                        update_data["notes"] = notes
                    
                    # 处理时间更新
                    if appointment_date is not None:
                        # 先尝试不使用LLM解析（快速路径），如果失败再使用LLM
                        timestamp, date, _ = await parse_datetime_with_llm(appointment_date, llm=None)
                        try:
                            if 'Z' in timestamp:
                                new_appointment_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            else:
                                new_appointment_date = datetime.fromisoformat(timestamp)
                        except ValueError:
                            # 如果解析失败，使用当前时间
                            new_appointment_date = datetime.now()
                        
                        # 验证预约时间
                        is_valid, validation_msg = validate_appointment_date(new_appointment_date)
                        if not is_valid:
                            return validation_msg
                        
                        update_data["appointment_date"] = new_appointment_date
                    
                    # 更新记录
                    db_obj = await crud_appointment.update(session, db_obj, update_data)
                    await session.commit()
                    
                    new_appointment_date = update_data.get("appointment_date", db_obj.appointment_date)
                    new_department = update_data.get("department", db_obj.department)
                    new_doctor_id = update_data.get("doctor_id", db_obj.doctor_id)
                    new_doctor_name = update_data.get("doctor_name", db_obj.doctor_name)
                    new_status = update_data.get("status", db_obj.status)
                    
                except Exception as e:
                    await session.rollback()
                    raise
            
            logger.info(f"成功更新用户 {user_id} 的预约记录: ID={appointment_id}")
            
            date_str = new_appointment_date.strftime('%Y-%m-%d')
            time_str = new_appointment_date.strftime('%Y-%m-%d %H:%M:%S')
            status_map = {
                'pending': '待处理',
                'completed': '已完成',
                'cancelled': '已取消'
            }
            status_str = status_map.get(new_status, new_status)
            doctor_info = f"，医生：{new_doctor_name or new_doctor_id}" if (new_doctor_name or new_doctor_id) else ""
            
            return f"成功更新预约记录：预约编号 {appointment_id}，科室：{new_department}{doctor_info}，预约时间：{time_str}，状态：{status_str}。"
            
        except Exception as e:
            logger.error(f"更新预约记录失败: {str(e)}")
            return f"更新预约记录时发生错误: {str(e)}"
    
    return [appointment_booking, query_appointment, update_appointment]
