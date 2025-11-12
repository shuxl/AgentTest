/**
 * 数据展示页面
 */
import { Layout } from 'antd';
import MainLayout from '@/components/Layout/MainLayout';
import HealthStatus from '@/components/Dashboard/HealthStatus';
import StatsCard from '@/components/Dashboard/StatsCard';
import ConnectionPoolChart from '@/components/Dashboard/ConnectionPoolChart';

const { Content } = Layout;

function DashboardPage() {
  return (
    <MainLayout>
      <Content style={{ padding: '24px' }}>
        <HealthStatus />
        <StatsCard />
        <ConnectionPoolChart />
      </Content>
    </MainLayout>
  );
}

export default DashboardPage;

