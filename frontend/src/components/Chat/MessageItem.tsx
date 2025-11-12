/**
 * 消息项组件
 */
import { Card, Tag } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import { Message } from '@/types/chat';
import { formatTimestamp } from '@/utils/formatters';

interface MessageItemProps {
  message: Message;
}

function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
      }}
    >
      <Card
        style={{
          maxWidth: '70%',
          background: isUser ? '#1890ff' : '#f0f0f0',
          color: isUser ? '#fff' : '#000',
        }}
        bodyStyle={{ padding: '12px' }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
          {isUser ? <UserOutlined /> : <RobotOutlined />}
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: '4px' }}>{message.content}</div>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>
              {formatTimestamp(message.timestamp)}
            </div>
            {message.currentAgent && (
              <Tag color="blue" style={{ marginTop: '4px' }}>
                {message.currentAgent}
              </Tag>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

export default MessageItem;

