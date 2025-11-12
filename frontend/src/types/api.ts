/**
 * API 相关类型定义
 */

// 聊天请求
export interface ChatRequest {
  message: string;
  session_id: string;
  user_id: string;
}

// 聊天响应
export interface ChatResponse {
  response: string;
  current_intent: 'blood_pressure' | 'appointment' | 'doctor_assistant' | 'unclear';
  current_agent: string | null;
}

// 健康检查响应
export interface HealthResponse {
  status: string;
  message: string;
}

// 数据库健康检查响应
export interface DatabaseHealthResponse {
  status: 'ok' | 'degraded' | 'error';
  langgraph_pool: 'ok' | 'not_initialized';
  sqlalchemy_engine: 'ok' | 'not_initialized';
  pool_stats: PoolStats;
  message?: string;
}

// 连接池统计信息
export interface PoolStats {
  langgraph_pool: LangGraphPoolStats | null;
  sqlalchemy_engine: SqlAlchemyPoolStats | null;
}

// LangGraph连接池统计
export interface LangGraphPoolStats {
  min_size: number;
  max_size: number;
  pool_size: number;
  available: number;
  waiting: number;
}

// SQLAlchemy连接池统计
export interface SqlAlchemyPoolStats {
  size: number;
  checked_in: number;
  checked_out: number;
  overflow: number;
  invalid: number;
}

// API错误响应
export interface ApiErrorResponse {
  detail: string;
}

