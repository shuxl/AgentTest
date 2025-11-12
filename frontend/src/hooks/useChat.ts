/**
 * 聊天相关Hook
 */
import { useCallback } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { chatService } from '@/services/chatService';
import { DEFAULT_USER_ID } from '@/utils/constants';
import { isValidMessage } from '@/utils/validators';

export function useChat() {
  const {
    currentSessionId,
    messages,
    isLoading,
    error,
    addMessage,
    setLoading,
    setError,
    createSession,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!isValidMessage(content)) {
        return;
      }

      if (!currentSessionId) {
        createSession();
        return;
      }

      setLoading(true);
      setError(null);

      // 添加用户消息
      addMessage({
        content: content.trim(),
        role: 'user',
      });

      try {
        const response = await chatService.sendMessage(
          content.trim(),
          currentSessionId,
          DEFAULT_USER_ID
        );

        // 添加助手回复
        addMessage({
          content: response.response,
          role: 'assistant',
          currentIntent: response.current_intent,
          currentAgent: response.current_agent,
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '发送消息失败';
        setError(errorMessage);
        addMessage({
          content: '抱歉，消息发送失败，请稍后重试。',
          role: 'system',
        });
      } finally {
        setLoading(false);
      }
    },
    [currentSessionId, addMessage, setLoading, setError, createSession]
  );

  return {
    messages,
    isLoading,
    error,
    sendMessage,
  };
}

