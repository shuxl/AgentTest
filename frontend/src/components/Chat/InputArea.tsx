/**
 * 输入区域组件
 */
import { useState, KeyboardEvent } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { useChatStore } from '@/stores/chatStore';
import { chatService } from '@/services/chatService';
import { DEFAULT_USER_ID } from '@/utils/constants';
import { isValidMessage } from '@/utils/validators';

const { TextArea } = Input;

function InputArea() {
  const [inputValue, setInputValue] = useState('');
  const { currentSessionId, addMessage, setLoading, setError, createSession } = useChatStore();

  const handleSend = async () => {
    if (!isValidMessage(inputValue)) {
      return;
    }

    if (!currentSessionId) {
      createSession();
      return;
    }

    const userMessage = inputValue.trim();
    setInputValue('');
    setLoading(true);
    setError(null);

    // 添加用户消息
    addMessage({
      content: userMessage,
      role: 'user',
    });

    try {
      const response = await chatService.sendMessage(
        userMessage,
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
    } catch (error) {
      setError(error instanceof Error ? error.message : '发送消息失败');
      // 添加错误消息
      addMessage({
        content: '抱歉，消息发送失败，请稍后重试。',
        role: 'system',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
      <div style={{ display: 'flex', gap: '8px' }}>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入消息... (Enter发送, Shift+Enter换行)"
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!isValidMessage(inputValue)}
        >
          发送
        </Button>
      </div>
    </div>
  );
}

export default InputArea;

