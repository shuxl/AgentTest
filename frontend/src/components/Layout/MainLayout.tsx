/**
 * 主布局组件
 */
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { MessageOutlined, DashboardOutlined } from '@ant-design/icons';
import Header from './Header';

const { Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

function MainLayout({ children }: MainLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '聊天',
    },
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '数据展示',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Header />
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout style={{ padding: '0' }}>
          <Content style={{ margin: 0, background: '#fff' }}>
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default MainLayout;

