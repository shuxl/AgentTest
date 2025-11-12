/**
 * 常量定义
 */

// API配置
export const API_TIMEOUT = {
  CHAT: 60000, // 60秒
  HEALTH: 5000, // 5秒
};

// 用户ID（可以从localStorage或配置中获取）
export const DEFAULT_USER_ID = 'user_123';

// 意图类型
export const INTENT_TYPES = {
  BLOOD_PRESSURE: 'blood_pressure',
  APPOINTMENT: 'appointment',
  DOCTOR_ASSISTANT: 'doctor_assistant',
  UNCLEAR: 'unclear',
} as const;

// 智能体名称
export const AGENT_NAMES = {
  BLOOD_PRESSURE: 'blood_pressure_agent',
  APPOINTMENT: 'appointment_agent',
  DOCTOR_ASSISTANT: 'doctor_assistant_agent',
} as const;

// 自动刷新间隔（毫秒）
export const AUTO_REFRESH_INTERVAL = 5000;

