/**
 * 统计卡片组件
 */
import { Card, Row, Col, Statistic } from 'antd';
import { useDashboardStore } from '@/stores/dashboardStore';

function StatsCard() {
  const { healthStatus } = useDashboardStore();

  const langgraphPool = healthStatus?.pool_stats?.langgraph_pool;
  const sqlalchemyPool = healthStatus?.pool_stats?.sqlalchemy_engine;

  return (
    <Card title="连接池统计" style={{ marginTop: '16px' }}>
      <Row gutter={16}>
        <Col span={12}>
          <Card>
            <h3>LangGraph连接池</h3>
            {langgraphPool ? (
              <>
                <Statistic title="最小连接数" value={langgraphPool.min_size} />
                <Statistic title="最大连接数" value={langgraphPool.max_size} />
                <Statistic title="当前连接数" value={langgraphPool.pool_size} />
                <Statistic title="可用连接数" value={langgraphPool.available} />
                <Statistic title="等待连接数" value={langgraphPool.waiting} />
              </>
            ) : (
              <div>暂无数据</div>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <h3>SQLAlchemy连接池</h3>
            {sqlalchemyPool ? (
              <>
                <Statistic title="连接池大小" value={sqlalchemyPool.size} />
                <Statistic title="已归还" value={sqlalchemyPool.checked_in} />
                <Statistic title="已借出" value={sqlalchemyPool.checked_out} />
                <Statistic title="溢出连接" value={sqlalchemyPool.overflow} />
                <Statistic title="无效连接" value={sqlalchemyPool.invalid} />
              </>
            ) : (
              <div>暂无数据</div>
            )}
          </Card>
        </Col>
      </Row>
    </Card>
  );
}

export default StatsCard;

