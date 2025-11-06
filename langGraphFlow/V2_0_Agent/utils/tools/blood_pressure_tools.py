"""
血压记录工具实现
包含record_blood_pressure、query_blood_pressure、update_blood_pressure、info工具
使用PostgreSQL数据库表blood_pressure_records存储，符合设计文档要求
"""
import logging
from typing import Optional
from langchain_core.tools import tool
from datetime import datetime
import re
from psycopg_pool import AsyncConnectionPool
from langgraph.store.postgres import AsyncPostgresStore

logger = logging.getLogger(__name__)


def validate_blood_pressure(systolic: int, diastolic: int) -> tuple[bool, str]:
    """
    验证血压数据
    
    Args:
        systolic: 收缩压
        diastolic: 舒张压
    
    Returns:
        (is_valid, message): 验证结果和消息
    """
    # 范围检查（根据设计文档：收缩压50-300，舒张压30-200）
    if not (50 <= systolic <= 300):
        return False, f"收缩压 {systolic} mmHg 超出合理范围（50-300）。请确认数据是否正确。"
    
    if not (30 <= diastolic <= 200):
        return False, f"舒张压 {diastolic} mmHg 超出合理范围（30-200）。请确认数据是否正确。"
    
    # 逻辑检查
    if systolic <= diastolic:
        return False, f"收缩压 {systolic} 必须大于舒张压 {diastolic}。请确认数据是否正确。"
    
    # 健康提示
    warnings = []
    if systolic > 140:
        warnings.append("收缩压偏高，建议关注")
    if diastolic > 90:
        warnings.append("舒张压偏高，建议关注")
    if systolic < 90:
        warnings.append("收缩压偏低，建议关注")
    if diastolic < 60:
        warnings.append("舒张压偏低，建议关注")
    
    warning_msg = "。".join(warnings) if warnings else ""
    
    return True, warning_msg


async def parse_datetime_with_llm(date_str: Optional[str], llm=None) -> tuple[str, str, str]:
    """
    使用LLM解析日期时间字符串，支持相对时间（如"本周一"、"昨天"等）
    
    Args:
        date_str: 日期时间字符串（支持多种格式，包括相对时间）
        llm: LLM实例（可选），如果为None则自动获取
    
    Returns:
        (timestamp, date, original_description): ISO格式的时间戳、日期字符串和原始描述
    """
    from langchain_core.prompts import ChatPromptTemplate
    from ..llms import get_llm_by_config
    
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
            "%Y/%m/%d",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat(), dt.strftime("%Y-%m-%d"), original_description
            except ValueError:
                continue
    except Exception:
        pass
    
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


def parse_datetime(date_str: Optional[str]) -> tuple[str, str]:
    """
    解析日期时间字符串，转换为ISO格式的时间戳和日期（兼容旧接口）
    
    注意：此函数不支持相对时间解析，建议使用parse_datetime_with_llm
    
    Args:
        date_str: 日期时间字符串（支持标准格式）
    
    Returns:
        (timestamp, date): ISO格式的时间戳和日期字符串
    """
    if date_str is None:
        now = datetime.now()
        return now.isoformat(), now.strftime("%Y-%m-%d")
    
    try:
        # 尝试解析标准日期时间格式
        if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
            # 标准日期格式 YYYY-MM-DD
            if len(date_str) == 10:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                # 带时间的格式
                dt = datetime.fromisoformat(date_str.replace(' ', 'T'))
            return dt.isoformat(), dt.strftime("%Y-%m-%d")
        
        # 尝试其他常见格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat(), dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # 如果都解析失败，使用当前时间
        logger.warning(f"日期解析失败: {date_str}，使用当前时间")
        now = datetime.now()
        return now.isoformat(), now.strftime("%Y-%m-%d")
        
    except Exception as e:
        logger.warning(f"日期解析失败: {date_str}, 错误: {e}，使用当前时间")
        now = datetime.now()
        return now.isoformat(), now.strftime("%Y-%m-%d")


def create_blood_pressure_tools(pool: AsyncConnectionPool, user_id: str, store: Optional[AsyncPostgresStore] = None):
    """
    创建血压记录相关的工具
    
    Args:
        pool: PostgreSQL数据库连接池实例，用于访问blood_pressure_records表
        user_id: 用户ID
        store: PostgreSQL Store实例（可选），用于查询用户设置信息（长期记忆）
    
    Returns:
        List[BaseTool]: 工具列表
    """
    
    @tool("record_blood_pressure", description="记录用户的血压数据到数据库表blood_pressure_records。date_time参数用于解析和存储标准时间，original_time_description参数用于保存用户的原始时间描述（如'今天早上8点'、'昨天下午'等）。")
    async def record_blood_pressure(
        systolic: int,
        diastolic: int,
        date_time: Optional[str] = None,
        original_time_description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        记录用户的血压数据
        
        Args:
            systolic: 收缩压（mmHg），范围50-300
            diastolic: 舒张压（mmHg），范围30-200
            date_time: 测量日期时间（支持多种格式，如"今天早上8点"、"2024-01-15 08:00"等），可选，默认当前时间
                       工具会自动解析为标准时间并存储到measurement_time字段
            original_time_description: 用户的原始时间描述（可选），用于保存用户原始的时间描述（如"今天早上8点"、"昨天下午"等）
                                      如果提供了此参数，将保存到original_time_description字段
            notes: 备注信息，可选
        
        Returns:
            str: 保存结果消息
        """
        try:
            # 数据验证
            is_valid, validation_msg = validate_blood_pressure(systolic, diastolic)
            if not is_valid:
                return validation_msg
            
            # 解析日期时间（使用LLM支持相对时间解析）
            from ..llms import get_llm_by_config
            llm = get_llm_by_config()
            timestamp, date, _ = await parse_datetime_with_llm(date_time, llm)
            
            # 将ISO格式的时间戳转换为PostgreSQL TIMESTAMP格式
            try:
                if 'Z' in timestamp:
                    measurement_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    measurement_time = datetime.fromisoformat(timestamp)
            except ValueError:
                # 如果解析失败，使用当前时间
                measurement_time = datetime.now()
            
            # 插入到数据库表（包含原始时间描述）
            # 使用智能体提供的original_time_description参数，如果没有提供则使用None
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO blood_pressure_records 
                        (user_id, systolic, diastolic, measurement_time, original_time_description, notes)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, systolic, diastolic, measurement_time, 
                          original_time_description if original_time_description else None, notes or ""))
                    
                    result = await cur.fetchone()
                    record_id = result['id'] if result else None
            
            logger.info(f"成功为用户 {user_id} 保存血压记录: ID={record_id}, systolic={systolic}, diastolic={diastolic}")
            
            # 构造返回消息
            health_msg = ""
            if systolic > 140 or diastolic > 90:
                health_msg = "您的血压值偏高，建议关注健康。"
            elif systolic < 90 or diastolic < 60:
                health_msg = "您的血压值偏低，建议关注健康。"
            else:
                health_msg = "您的血压值在正常范围内，继续保持良好的生活习惯。"
            
            return f"成功保存血压记录：收缩压 {systolic} mmHg，舒张压 {diastolic} mmHg，测量日期 {date}，测量时间 {measurement_time.strftime('%Y-%m-%d %H:%M:%S')}。{health_msg}"
            
        except Exception as e:
            logger.error(f"保存血压记录失败: {str(e)}")
            return f"保存血压记录时发生错误: {str(e)}"
    
    @tool("query_blood_pressure", description="查询用户的历史血压记录")
    async def query_blood_pressure(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """
        查询用户的历史血压记录
        
        Args:
            start_date: 开始日期（ISO格式），可选
            end_date: 结束日期（ISO格式），可选
            limit: 返回记录数量限制，默认10
        
        Returns:
            str: 查询结果，格式化的血压记录列表
        """
        try:
            # 从数据库表查询数据
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # 构建查询SQL（包含原始时间描述）
                    query = """
                        SELECT id, systolic, diastolic, measurement_time, original_time_description, notes, created_at
                        FROM blood_pressure_records
                        WHERE user_id = %s
                    """
                    params = [user_id]
                    
                    # 添加时间过滤条件
                    if start_date:
                        query += " AND DATE(measurement_time) >= %s"
                        params.append(start_date)
                    if end_date:
                        query += " AND DATE(measurement_time) <= %s"
                        params.append(end_date)
                    
                    # 按时间排序（最新的在前）并限制数量
                    query += " ORDER BY measurement_time DESC LIMIT %s"
                    params.append(limit)
                    
                    await cur.execute(query, params)
                    rows = await cur.fetchall()
            
            if not rows:
                return "未找到历史血压记录。"
            
            # 格式化返回结果
            result_lines = [f"找到 {len(rows)} 条血压记录：\n"]
            for idx, row in enumerate(rows, 1):
                systolic = row['systolic']
                diastolic = row['diastolic']
                measurement_time = row['measurement_time']
                original_time_desc = row.get('original_time_description') or ""
                notes = row['notes'] or ""
                
                date_str = measurement_time.strftime('%Y-%m-%d')
                time_str = measurement_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 如果有原始时间描述，显示原始描述
                time_desc_str = f"（用户描述：{original_time_desc}）" if original_time_desc else ""
                notes_str = f"，备注：{notes}" if notes else ""
                
                result_lines.append(f"{idx}. 收缩压：{systolic} mmHg，舒张压：{diastolic} mmHg，日期：{date_str}，时间：{time_str}{time_desc_str}{notes_str}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"查询血压记录失败: {str(e)}")
            return f"查询血压记录时发生错误: {str(e)}"
    
    @tool("update_blood_pressure", description="更新已存在的血压记录。date_time参数用于解析和存储标准时间，original_time_description参数用于保存用户的原始时间描述（如'今天早上8点'、'昨天下午'等）。")
    async def update_blood_pressure(
        record_id: str,
        systolic: Optional[int] = None,
        diastolic: Optional[int] = None,
        date_time: Optional[str] = None,
        original_time_description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        更新已存在的血压记录
        
        Args:
            record_id: 记录ID（需要包含record_前缀）
            systolic: 新的收缩压，可选
            diastolic: 新的舒张压，可选
            date_time: 新的测量日期时间，可选
            notes: 新的备注，可选
        
        Returns:
            str: 更新结果消息
        """
        try:
            # 查找记录
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    # 检查记录是否存在
                    await cur.execute("""
                        SELECT id, systolic, diastolic, measurement_time, notes
                        FROM blood_pressure_records
                        WHERE id = %s AND user_id = %s
                    """, (int(record_id) if record_id.isdigit() else None, user_id))
                    
                    row = await cur.fetchone()
                    
                    if not row:
                        return f"未找到ID为 {record_id} 的血压记录。"
                    
                    # 获取当前值
                    current_systolic = row['systolic']
                    current_diastolic = row['diastolic']
                    current_measurement_time = row['measurement_time']
                    current_notes = row['notes'] or ""
                    
                    # 更新字段
                    new_systolic = systolic if systolic is not None else current_systolic
                    new_diastolic = diastolic if diastolic is not None else current_diastolic
                    new_notes = notes if notes is not None else current_notes
                    
                    # 处理时间更新
                    if date_time is not None:
                        # 使用LLM解析相对时间
                        from ..llms import get_llm_by_config
                        llm = get_llm_by_config()
                        timestamp, date, _ = await parse_datetime_with_llm(date_time, llm)
                        try:
                            if 'Z' in timestamp:
                                new_measurement_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            else:
                                new_measurement_time = datetime.fromisoformat(timestamp)
                        except ValueError:
                            # 如果解析失败，使用当前时间
                            new_measurement_time = datetime.now()
                    else:
                        new_measurement_time = current_measurement_time
                    
                    # 验证更新后的数据
                    is_valid, validation_msg = validate_blood_pressure(new_systolic, new_diastolic)
                    if not is_valid:
                        return validation_msg
                    
                    # 更新数据库记录
                    # 如果date_time不为None，更新measurement_time和original_time_description
                    # 使用智能体提供的original_time_description参数
                    if date_time is not None:
                        await cur.execute("""
                            UPDATE blood_pressure_records
                            SET systolic = %s, diastolic = %s, measurement_time = %s, 
                                original_time_description = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s AND user_id = %s
                        """, (new_systolic, new_diastolic, new_measurement_time, 
                              original_time_description if original_time_description else None, new_notes, 
                              int(record_id) if record_id.isdigit() else None, user_id))
                    else:
                        # 不更新measurement_time和original_time_description，保持原有值
                        await cur.execute("""
                            UPDATE blood_pressure_records
                            SET systolic = %s, diastolic = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s AND user_id = %s
                        """, (new_systolic, new_diastolic, new_notes, 
                              int(record_id) if record_id.isdigit() else None, user_id))
            
            logger.info(f"成功更新用户 {user_id} 的血压记录: ID={record_id}, systolic={new_systolic}, diastolic={new_diastolic}")
            
            date_str = new_measurement_time.strftime('%Y-%m-%d')
            time_str = new_measurement_time.strftime('%Y-%m-%d %H:%M:%S')
            
            return f"成功更新血压记录：收缩压 {new_systolic} mmHg，舒张压 {new_diastolic} mmHg，日期 {date_str}，时间 {time_str}。"
            
        except Exception as e:
            logger.error(f"更新血压记录失败: {str(e)}")
            return f"更新血压记录时发生错误: {str(e)}"
    
    @tool("info", description="查询用户的基础信息，包括setting信息和血压信息统计")
    async def info() -> str:
        """
        查询用户的基础信息
        
        Returns:
            str: 格式化的用户信息，包括setting信息和血压信息统计
        """
        try:
            result_lines = []
            
            # 1. 查询setting信息（从store的memories命名空间）
            # 注意：用户设置信息仍然使用store存储，因为它是非结构化数据
            result_lines.append("=== 用户设置信息 ===")
            if store:
                namespace_settings = ("memories", user_id)
                settings_memories = await store.asearch(namespace_settings, query="")
                
                if settings_memories:
                    for memory in settings_memories:
                        try:
                            if isinstance(memory.value, dict) and "data" in memory.value:
                                setting_data = memory.value["data"]
                                result_lines.append(f"- {setting_data}")
                        except Exception as e:
                            logger.warning(f"解析设置信息失败: {e}")
                            continue
                else:
                    result_lines.append("暂无设置信息")
            else:
                result_lines.append("（用户设置信息存储在长期记忆中，当前未配置store）")
            result_lines.append("")
            
            # 2. 查询血压信息统计（从数据库表）
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT systolic, diastolic, measurement_time, original_time_description, notes
                        FROM blood_pressure_records
                        WHERE user_id = %s
                        ORDER BY measurement_time DESC
                    """, (user_id,))
                    
                    rows = await cur.fetchall()
            
            result_lines.append("=== 血压信息统计 ===")
            
            if not rows:
                result_lines.append("暂无血压记录")
            else:
                # 统计信息
                total_records = len(rows)
                
                # 计算平均值、最高值、最低值
                systolic_values = [row['systolic'] for row in rows]
                diastolic_values = [row['diastolic'] for row in rows]
                
                avg_systolic = sum(systolic_values) / len(systolic_values) if systolic_values else 0
                avg_diastolic = sum(diastolic_values) / len(diastolic_values) if diastolic_values else 0
                
                max_systolic = max(systolic_values) if systolic_values else 0
                min_systolic = min(systolic_values) if systolic_values else 0
                max_diastolic = max(diastolic_values) if diastolic_values else 0
                min_diastolic = min(diastolic_values) if diastolic_values else 0
                
                # 获取最新记录
                latest_record = rows[0] if rows else None
                
                result_lines.append(f"总记录数：{total_records} 条")
                result_lines.append(f"平均收缩压：{avg_systolic:.1f} mmHg")
                result_lines.append(f"平均舒张压：{avg_diastolic:.1f} mmHg")
                result_lines.append(f"最高收缩压：{max_systolic} mmHg")
                result_lines.append(f"最低收缩压：{min_systolic} mmHg")
                result_lines.append(f"最高舒张压：{max_diastolic} mmHg")
                result_lines.append(f"最低舒张压：{min_diastolic} mmHg")
                
                if latest_record:
                    latest_date = latest_record['measurement_time'].strftime('%Y-%m-%d')
                    result_lines.append(f"\n最新记录：")
                    result_lines.append(f"  日期：{latest_date}")
                    result_lines.append(f"  收缩压：{latest_record['systolic']} mmHg")
                    result_lines.append(f"  舒张压：{latest_record['diastolic']} mmHg")
                    if latest_record['notes']:
                        result_lines.append(f"  备注：{latest_record['notes']}")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"查询用户信息失败: {str(e)}")
            return f"查询用户信息时发生错误: {str(e)}"
    
    return [record_blood_pressure, query_blood_pressure, update_blood_pressure, info]

