/**
 * 连接池图表组件
 */
import { Card } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useDashboardStore } from '@/stores/dashboardStore';

function ConnectionPoolChart() {
  const { healthStatus } = useDashboardStore();

  const langgraphPool = healthStatus?.pool_stats?.langgraph_pool;
  const sqlalchemyPool = healthStatus?.pool_stats?.sqlalchemy_engine;

  const langgraphOption = {
    title: {
      text: 'LangGraph连接池使用情况',
    },
    tooltip: {},
    xAxis: {
      data: ['最小', '最大', '当前', '可用', '等待'],
    },
    yAxis: {},
    series: [
      {
        name: '连接数',
        type: 'bar',
        data: langgraphPool
          ? [
              langgraphPool.min_size,
              langgraphPool.max_size,
              langgraphPool.pool_size,
              langgraphPool.available,
              langgraphPool.waiting,
            ]
          : [],
      },
    ],
  };

  const sqlalchemyOption = {
    title: {
      text: 'SQLAlchemy连接池使用情况',
    },
    tooltip: {},
    xAxis: {
      data: ['总大小', '已归还', '已借出', '溢出', '无效'],
    },
    yAxis: {},
    series: [
      {
        name: '连接数',
        type: 'bar',
        data: sqlalchemyPool
          ? [
              sqlalchemyPool.size,
              sqlalchemyPool.checked_in,
              sqlalchemyPool.checked_out,
              sqlalchemyPool.overflow,
              sqlalchemyPool.invalid,
            ]
          : [],
      },
    ],
  };

  return (
    <Card title="连接池图表" style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', gap: '16px' }}>
        <div style={{ flex: 1 }}>
          <ReactECharts option={langgraphOption} style={{ height: '300px' }} />
        </div>
        <div style={{ flex: 1 }}>
          <ReactECharts option={sqlalchemyOption} style={{ height: '300px' }} />
        </div>
      </div>
    </Card>
  );
}

export default ConnectionPoolChart;

