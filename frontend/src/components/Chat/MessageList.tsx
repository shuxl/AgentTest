/**
 * 消息列表组件
 */
import { useEffect, useRef } from 'react';
import { List, Empty } from 'antd';
import { useChatStore } from '@/stores/chatStore';
import MessageItem from './MessageItem';

function MessageList() {
  const { messages } = useChatStore();
  const listRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty description="还没有消息，开始对话吧" />
      </div>
    );
  }

  return (
    <div
      ref={listRef}
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
      }}
    >
      <List
        dataSource={messages}
        renderItem={(message) => <MessageItem message={message} />}
      />
    </div>
  );
}

export default MessageList;

