/**
 * 聊天相关类型定义
 */

// 消息角色
export type MessageRole = 'user' | 'assistant' | 'system';

// 消息接口
export interface Message {
  id: string;
  content: string;
  role: MessageRole;
  timestamp: number;
  currentIntent?: string;
  currentAgent?: string | null;
}

// 会话接口
export interface Session {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messageCount: number;
}

// 聊天状态
export interface ChatState {
  sessions: Session[];
  currentSessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

