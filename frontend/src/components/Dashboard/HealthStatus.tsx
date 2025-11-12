/**
 * 健康状态组件
 */
import { Card, Tag, Space } from 'antd';
import { useEffect } from 'react';
import { useDashboardStore } from '@/stores/dashboardStore';
import { healthService } from '@/services/healthService';
import { AUTO_REFRESH_INTERVAL } from '@/utils/constants';

function HealthStatus() {
  const { healthStatus, isLoading, autoRefresh, setHealthStatus, setLoading } =
    useDashboardStore();

  const fetchHealthStatus = async () => {
    setLoading(true);
    try {
      const status = await healthService.checkDatabaseHealth();
      setHealthStatus(status);
    } catch (error) {
      console.error('获取健康状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthStatus();

    if (autoRefresh) {
      const interval = setInterval(fetchHealthStatus, AUTO_REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card title="系统健康状态" loading={isLoading}>
      {healthStatus && (
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <strong>总体状态：</strong>
            <Tag color={getStatusColor(healthStatus.status)}>
              {healthStatus.status}
            </Tag>
          </div>
          <div>
            <strong>LangGraph连接池：</strong>
            <Tag color={healthStatus.langgraph_pool === 'ok' ? 'success' : 'error'}>
              {healthStatus.langgraph_pool}
            </Tag>
          </div>
          <div>
            <strong>SQLAlchemy引擎：</strong>
            <Tag color={healthStatus.sqlalchemy_engine === 'ok' ? 'success' : 'error'}>
              {healthStatus.sqlalchemy_engine}
            </Tag>
          </div>
        </Space>
      )}
    </Card>
  );
}

export default HealthStatus;

