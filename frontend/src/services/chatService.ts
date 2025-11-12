/**
 * 聊天服务
 */
import api from './api';
import { ChatRequest, ChatResponse } from '../types/api';
import { API_TIMEOUT } from '../utils/constants';

export const chatService = {
  /**
   * 发送消息
   */
  async sendMessage(
    message: string,
    sessionId: string,
    userId: string
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      session_id: sessionId,
      user_id: userId,
    };

    const response = await api.post<ChatResponse>('/api/chat', request, {
      timeout: API_TIMEOUT.CHAT,
    });
    return response.data;
  },
};

