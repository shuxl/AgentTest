/**
 * 头部组件
 */
import { Layout } from 'antd';

const { Header: AntHeader } = Layout;

function Header() {
  return (
    <AntHeader
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        borderBottom: '1px solid #f0f0f0',
      }}
    >
      <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
        LangGraph Agent
      </h1>
    </AntHeader>
  );
}

export default Header;

