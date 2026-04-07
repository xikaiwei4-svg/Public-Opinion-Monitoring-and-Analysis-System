import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchOpinionTrend, selectOpinionTrend, selectTrendLoading } from '../store/features/trendSlice';
import { Card, Typography } from 'antd';

const { Title, Text, Paragraph } = Typography;

const TestTrendDataNew: React.FC = () => {
  const dispatch = useDispatch();
  const opinionTrend = useSelector(selectOpinionTrend);
  const loading = useSelector(selectTrendLoading);

  useEffect(() => {
    // 获取趋势数据
    dispatch(fetchOpinionTrend({ days: '7' }));
  }, [dispatch]);

  return (
    <div style={{ padding: '20px' }}>
      <Title level={4}>趋势数据测试</Title>
      <div>测试组件已加载</div>
      <div>加载状态: {loading ? '加载中' : '已完成'}</div>
      <div>数据类型: {typeof opinionTrend}</div>
    </div>
  );
};

export default TestTrendDataNew;