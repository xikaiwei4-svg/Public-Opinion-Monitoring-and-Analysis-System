import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchOpinionTrend, selectOpinionTrend, selectTrendLoading } from '../store/features/trendSlice';
import { Card, Typography } from 'antd';

const { Title, Text, Paragraph } = Typography;

const TestTrendData: React.FC = () => {
  const dispatch = useDispatch();
  const opinionTrend = useSelector(selectOpinionTrend);
  const loading = useSelector(selectTrendLoading);

  useEffect(() => {
    // 获取趋势数据
    dispatch(fetchOpinionTrend({ days: '7' }));
  }, [dispatch]);

  return (
    <div className="fade-in" style={{ padding: '20px' }}>
      <Title level={4}>趋势数据测试</Title>
      
      <Card title="数据加载状态">
        <Text>加载中: {loading ? '是' : '否'}</Text>
      </Card>

      <Card title="opinionTrend 数据类型" style={{ marginTop: '16px' }}>
        <Text>类型: {typeof opinionTrend}</Text>
        <Paragraph>是否为数组: {Array.isArray(opinionTrend) ? '是' : '否'}</Paragraph>
        <Paragraph>数组长度: {Array.isArray(opinionTrend) ? opinionTrend.length : 'N/A'}</Paragraph>
      </Card>

      {Array.isArray(opinionTrend) && (
        <Card title="数据内容" style={{ marginTop: '16px' }}>
          <Paragraph>
            <pre>{JSON.stringify(opinionTrend, null, 2)}</pre>
          </Paragraph>
        </Card>
      )}

      {Array.isArray(opinionTrend) && opinionTrend.length > 0 && (
        <Card title="第一个元素结构" style={{ marginTop: '16px' }}>
          <Paragraph>
            <pre>{JSON.stringify(opinionTrend[0], null, 2)}</pre>
          </Paragraph>
        </Card>
      )}

      {/* 测试直接访问count属性 */}
      {Array.isArray(opinionTrend) && opinionTrend.length > 0 && (
        <Card title="直接访问count属性测试" style={{ marginTop: '16px' }}>
          <Paragraph>尝试访问第一个元素的count: 
            {opinionTrend[0] && typeof opinionTrend[0].count !== 'undefined' ? 
              opinionTrend[0].count : 'undefined'}
          </Paragraph>
          <Paragraph>尝试访问最后一个元素的count: 
            {opinionTrend[opinionTrend.length - 1] && typeof opinionTrend[opinionTrend.length - 1].count !== 'undefined' ? 
              opinionTrend[opinionTrend.length - 1].count : 'undefined'}
          </Paragraph>
        </Card>
      )}
    </div>
  );
};

export default TestTrendData;