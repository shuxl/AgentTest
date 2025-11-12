/**
 * 聊天页面
 */
import { useEffect } from 'react';
import { Layout } from 'antd';
import MainLayout from '@/components/Layout/MainLayout';
import ChatWindow from '@/components/Chat/ChatWindow';
import { useChatStore } from '@/stores/chatStore';

const { Content } = Layout;

function ChatPage() {
  const { currentSessionId, createSession } = useChatStore();

  useEffect(() => {
    // 如果没有当前会话，创建一个新会话
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  return (
    <MainLayout>
      <Content style={{ height: '100%', display: 'flex' }}>
        <ChatWindow />
      </Content>
    </MainLayout>
  );
}

export default ChatPage;

