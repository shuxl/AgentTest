/**
 * 聊天窗口组件
 */
import { Layout } from 'antd';
import MessageList from './MessageList';
import InputArea from './InputArea';

const { Sider, Content } = Layout;

function ChatWindow() {
  return (
    <Layout style={{ height: '100%' }}>
      <Sider width={250} style={{ background: '#fafafa', borderRight: '1px solid #f0f0f0' }}>
        {/* 会话列表区域 - 待实现 */}
        <div style={{ padding: '16px' }}>会话列表</div>
      </Sider>
      <Layout>
        <Content style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <MessageList />
          <InputArea />
        </Content>
      </Layout>
    </Layout>
  );
}

export default ChatWindow;

