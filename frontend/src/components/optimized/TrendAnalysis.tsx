import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, Typography, Select, Button, Space, Tag, Row, Col, Table, Alert, Modal, DatePicker, Checkbox, Input, Dropdown } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchOpinionTrend, 
  fetchSentimentTrend, 
  fetchPlatformDistribution, 
  selectOpinionTrend, 
  selectSentimentTrend, 
  selectPlatformDistribution, 
  selectTrendLoading, 
  selectTrendError, 
  setSelectedPlatform, 
  selectTrendSelectedPlatform 
} from '../../store/features/trendSlice';
import { ArrowUpOutlined, ArrowDownOutlined, SyncOutlined, ExportOutlined, EyeOutlined, LineChartOutlined, FilterOutlined } from '@ant-design/icons';
import ChartComponent from './ChartComponent';

const { Title, Text } = Typography;
const { Option } = Select;

interface TrendAnalysisProps {
  timeRange?: string;
  onTimeRangeChange?: (value: string) => void;
  type?: 'line' | 'area' | 'pie';
  data?: any[];
  xField?: string;
  yField?: string;
  yFields?: string[];
  height?: number;
  showCharts?: boolean;
  enableFilter?: boolean;
}

// 表格组件
const DataTable: React.FC<{
  columns: any[];
  dataSource: any[];
  loading: boolean;
  emptyText: string;
}> = React.memo(({ columns, dataSource, loading, emptyText }) => (
  <Table
    columns={columns}
    dataSource={dataSource}
    loading={loading}
    pagination={{ pageSize: 10 }}
    locale={{ emptyText }}
    size="small"
    scroll={{ x: 'max-content' }}
  />
));

const TrendAnalysis: React.FC<TrendAnalysisProps> = React.memo(({ 
  timeRange = '7', 
  onTimeRangeChange, 
  type, 
  data, 
  xField, 
  yField, 
  yFields, 
  height,
  showCharts = true,
  enableFilter = true
}) => {
  const dispatch = useDispatch();
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedSentiments, setSelectedSentiments] = useState<string[]>(['positive', 'neutral', 'negative']);
  
  // 只有在没有type和data时才订阅Redux状态
  const opinionTrend = !type && !data ? useSelector(selectOpinionTrend) : [];
  const sentimentTrend = !type && !data ? useSelector(selectSentimentTrend) : [];
  const platformDistribution = !type && !data ? useSelector(selectPlatformDistribution) : [];
  const loading = !type && !data ? useSelector(selectTrendLoading) : false;
  const error = !type && !data ? useSelector(selectTrendError) : null;
  const selectedPlatform = !type && !data ? useSelector(selectTrendSelectedPlatform) : null;
  
  // 获取数据
  useEffect(() => {
    if (!type && !data && !onTimeRangeChange) {
      console.log('获取趋势分析数据...');
      dispatch(fetchOpinionTrend({ days: timeRange as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchSentimentTrend({ days: timeRange as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchPlatformDistribution({ days: timeRange as '7' | '15' | '30' }));
    }
  }, [dispatch, type, data, onTimeRangeChange, timeRange, selectedPlatform]);

  // 使用实际数据
  const trendData = useMemo(() => Array.isArray(opinionTrend) ? opinionTrend : [], [opinionTrend]);
  const sentimentData = useMemo(() => Array.isArray(sentimentTrend) ? sentimentTrend : [], [sentimentTrend]);
  const platformDistData = useMemo(() => Array.isArray(platformDistribution) ? platformDistribution : [], [platformDistribution]);

  // 计算趋势变化
  const trendChange = useMemo(() => {
    if (trendData.length < 2) return { change: 0, percentage: 0 };
    const latest = trendData[trendData.length - 1].count;
    const previous = trendData[trendData.length - 2].count;
    const change = latest - previous;
    const percentage = previous > 0 ? (change / previous) * 100 : 0;
    return { change, percentage };
  }, [trendData]);

  // 计算统计指标
  const statistics = useMemo(() => {
    const totalCount = trendData.reduce((sum, item) => sum + item.count, 0);
    const avgDailyCount = trendData.length > 0 ? totalCount / trendData.length : 0;
    const maxCount = Math.max(...trendData.map(item => item.count));
    
    const sentimentStats = sentimentData.length > 0 ? {
      positive: sentimentData.reduce((sum, item) => sum + item.positive, 0),
      neutral: sentimentData.reduce((sum, item) => sum + item.neutral, 0),
      negative: sentimentData.reduce((sum, item) => sum + item.negative, 0)
    } : { positive: 0, neutral: 0, negative: 0 };
    
    return {
      totalCount,
      avgDailyCount: avgDailyCount.toFixed(1),
      maxCount,
      sentimentStats
    };
  }, [trendData, sentimentData]);

  // 处理时间范围变化
  const handleTimeRangeChange = useCallback((value: string) => {
    if (onTimeRangeChange) {
      onTimeRangeChange(value);
    } else {
      dispatch(fetchOpinionTrend({ days: value as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchSentimentTrend({ days: value as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchPlatformDistribution({ days: value as '7' | '15' | '30' }));
    }
  }, [dispatch, onTimeRangeChange, selectedPlatform]);

  // 处理平台选择
  const handlePlatformChange = useCallback((value: string | null) => {
    dispatch(setSelectedPlatform(value));
  }, [dispatch]);

  // 刷新数据
  const handleRefresh = useCallback(() => {
    dispatch(fetchOpinionTrend({ days: timeRange, platform: selectedPlatform || undefined }));
    dispatch(fetchSentimentTrend({ days: timeRange, platform: selectedPlatform || undefined }));
    dispatch(fetchPlatformDistribution({ days: timeRange }));
  }, [dispatch, timeRange, selectedPlatform]);

  // 导出数据
  const handleExportData = useCallback(() => {
    const exportData = {
      opinionTrend: trendData,
      sentimentTrend: sentimentData,
      platformDistribution: platformDistData,
      statistics: statistics,
      exportTime: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trend_data_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [trendData, sentimentData, platformDistData, statistics]);

  // 导出为CSV
  const handleExportCSV = useCallback(() => {
    const headers = ['日期', '舆情数量', '热度指数'];
    const csvContent = [
      headers.join(','),
      ...trendData.map(item => [item.date, item.count, item.heat].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trend_data_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [trendData]);

  // 应用筛选
  const handleApplyFilter = useCallback(() => {
    // 这里可以添加筛选逻辑
    setFilterModalVisible(false);
  }, []);

  // 渲染自定义表格
  const renderCustomTable = useCallback(() => {
    if (!data || !Array.isArray(data) || data.length === 0) return null;
    
    let columns: any[] = [];
    
    // 构建列
    columns.push({
      title: xField || '日期',
      dataIndex: xField || 'date',
      key: xField || 'date',
      render: (text: any, record: any) => record[xField || 'date'] || record.platform || record.name
    });
    
    if (type === 'line' && yField) {
      columns.push({
        title: yField,
        dataIndex: yField,
        key: yField
      });
    }
    
    if (type === 'area' && yFields) {
      yFields.forEach(field => {
        columns.push({
          title: field === 'positive' ? '正面' : field === 'negative' ? '负面' : field === 'neutral' ? '中性' : field,
          dataIndex: field,
          key: field
        });
      });
    }
    
    if (type === 'pie') {
      columns.push({
        title: '平台',
        dataIndex: 'platform',
        key: 'platform',
        render: (text: any, record: any) => record.platform || record.name
      });
      columns.push({
        title: '数量',
        dataIndex: 'count',
        key: 'count',
        render: (text: any, record: any) => record.count || record.value
      });
    }
    
    return (
      <div style={{ height: height || 300, width: '100%' }}>
        <DataTable
          columns={columns}
          dataSource={data.slice(0, 50)}
          loading={false}
          emptyText="暂无数据"
        />
      </div>
    );
  }, [type, data, xField, yField, yFields, height]);

  // 舆情趋势表格列配置
  const opinionTrendColumns = useMemo(() => [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime()
    },
    {
      title: '舆情数量',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count
    },
    {
      title: '热度指数',
      dataIndex: 'heat',
      key: 'heat',
      sorter: (a: any, b: any) => a.heat - b.heat
    }
  ], []);

  // 情感趋势表格列配置
  const sentimentTrendColumns = useMemo(() => [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      sorter: (a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime()
    },
    {
      title: '正面',
      dataIndex: 'positive',
      key: 'positive',
      sorter: (a: any, b: any) => a.positive - b.positive,
      render: (value: number) => <Tag color="green">{value}</Tag>
    },
    {
      title: '中性',
      dataIndex: 'neutral',
      key: 'neutral',
      sorter: (a: any, b: any) => a.neutral - b.neutral,
      render: (value: number) => <Tag color="blue">{value}</Tag>
    },
    {
      title: '负面',
      dataIndex: 'negative',
      key: 'negative',
      sorter: (a: any, b: any) => a.negative - b.negative,
      render: (value: number) => <Tag color="red">{value}</Tag>
    }
  ], []);

  // 平台分布表格列配置
  const platformDistributionColumns = useMemo(() => [
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform'
    },
    {
      title: '数量',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (value: number) => `${value}%`
    }
  ], []);

  // 如果提供了type和data，渲染指定类型的表格
  if (type && data) {
    try {
      return renderCustomTable();
    } catch (error) {
      console.error('表格渲染错误:', error);
      return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height || 300, width: '100%', color: '#999' }}>
          表格渲染失败
        </div>
      );
    }
  }

  // 否则渲染默认的趋势分析表格
  try {
    return (
      <div style={{ width: '100%' }}>
        <Card 
          title="趋势分析"
          extra={
            <Space size="middle">
              {/* 视图切换 */}
              {showCharts && (
                <Space>
                  <Button 
                    type={viewMode === 'table' ? 'primary' : 'default'}
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={() => setViewMode('table')}
                  >
                    表格视图
                  </Button>
                  <Button 
                    type={viewMode === 'chart' ? 'primary' : 'default'}
                    size="small"
                    icon={<LineChartOutlined />}
                    onClick={() => setViewMode('chart')}
                  >
                    图表视图
                  </Button>
                </Space>
              )}
              
              {/* 当有onTimeRangeChange时，不显示时间范围选择器和刷新按钮 */}
              {!onTimeRangeChange && (
                <>
                  <Select 
                    value={timeRange} 
                    style={{ width: 100 }} 
                    onChange={handleTimeRangeChange}
                  >
                    <Option value="7">7天</Option>
                    <Option value="14">14天</Option>
                    <Option value="30">30天</Option>
                  </Select>
                  <Button 
                    type="primary" 
                    size="small" 
                    icon={<SyncOutlined />}
                    onClick={handleRefresh}
                  >
                    刷新
                  </Button>
                  {enableFilter && (
                    <Button 
                      size="small" 
                      icon={<FilterOutlined />}
                      onClick={() => setFilterModalVisible(true)}
                    >
                      筛选
                    </Button>
                  )}
                  <Dropdown menu={{
                    items: [
                      { key: 'json', label: '导出JSON', onClick: handleExportData },
                      { key: 'csv', label: '导出CSV', onClick: handleExportCSV }
                    ]
                  }}>
                    <Button size="small" icon={<ExportOutlined />}>
                      导出
                    </Button>
                  </Dropdown>
                </>
              )}
              <Select 
                placeholder="选择平台"
                allowClear
                style={{ width: 120 }} 
                value={selectedPlatform} 
                onChange={handlePlatformChange}
              >
                {platformDistData.map(platform => (
                  <Option key={platform.platform} value={platform.platform}>
                    {platform.platform}
                  </Option>
                ))}
              </Select>
            </Space>
          }
        >
          {error && (
            <Alert 
              message="数据加载失败" 
              description={error} 
              type="error" 
              showIcon 
              style={{ marginBottom: '16px' }}
            />
          )}

          {/* 统计卡片 */}
          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Card size="small" title="总舆情数">
                <Text strong style={{ fontSize: '24px', color: '#1890ff' }}>{statistics.totalCount}</Text>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="日均舆情数">
                <Text strong style={{ fontSize: '24px', color: '#52c41a' }}>{statistics.avgDailyCount}</Text>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="最高日舆情数">
                <Text strong style={{ fontSize: '24px', color: '#faad14' }}>{statistics.maxCount}</Text>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small" title="趋势变化">
                <Text 
                  strong 
                  style={{ fontSize: '24px', color: trendChange.change >= 0 ? '#52c41a' : '#f5222d' }}
                >
                  {trendChange.percentage.toFixed(1)}%
                  {trendChange.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                </Text>
              </Card>
            </Col>
          </Row>

          {viewMode === 'table' ? (
            <>
              <Row gutter={16} style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', width: '100%' }}>
                  <Title level={5}>舆情数量趋势</Title>
                </div>
                
                <Col span={24}>
                  <DataTable
                    columns={opinionTrendColumns}
                    dataSource={trendData}
                    loading={loading}
                    emptyText="暂无舆情趋势数据"
                  />
                </Col>
              </Row>

              <Row gutter={16} style={{ marginBottom: '24px' }}>
                <Col span={24}>
                  <Title level={5}>情感分布趋势</Title>
                  <DataTable
                    columns={sentimentTrendColumns}
                    dataSource={sentimentData}
                    loading={loading}
                    emptyText="暂无情感趋势数据"
                  />
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={24}>
                  <Title level={5}>平台分布</Title>
                  <DataTable
                    columns={platformDistributionColumns}
                    dataSource={platformDistData}
                    loading={loading}
                    emptyText="暂无平台分布数据"
                  />
                </Col>
              </Row>
            </>
          ) : (
            <>
              <Row gutter={16} style={{ marginBottom: '24px' }}>
                <Col span={24}>
                  <ChartComponent type="line" data={trendData} height={300} title="舆情数量趋势" />
                </Col>
              </Row>

              <Row gutter={16} style={{ marginBottom: '24px' }}>
                <Col span={24}>
                  <ChartComponent type="bar" data={sentimentData} height={300} title="情感分布趋势" />
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={24}>
                  <ChartComponent type="pie" data={platformDistData} height={300} title="平台分布" />
                </Col>
              </Row>
            </>
          )}
        </Card>

        {/* 筛选模态框 */}
        <Modal
          title="数据筛选"
          open={filterModalVisible}
          onOk={handleApplyFilter}
          onCancel={() => setFilterModalVisible(false)}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text>日期范围：</Text>
              <DatePicker.RangePicker 
                style={{ width: '100%' }}
                onChange={(dates) => {
                  if (dates) {
                    setDateRange([dates[0]?.format('YYYY-MM-DD') || '', dates[1]?.format('YYYY-MM-DD') || '']);
                  } else {
                    setDateRange(null);
                  }
                }}
              />
            </div>
            
            <div>
              <Text>关键词搜索：</Text>
              <Input 
                placeholder="输入关键词"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
            </div>
            
            <div>
              <Text>情感类型：</Text>
              <Space>
                <Checkbox 
                  checked={selectedSentiments.includes('positive')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSentiments([...selectedSentiments, 'positive']);
                    } else {
                      setSelectedSentiments(selectedSentiments.filter(s => s !== 'positive'));
                    }
                  }}
                >
                  正面
                </Checkbox>
                <Checkbox 
                  checked={selectedSentiments.includes('neutral')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSentiments([...selectedSentiments, 'neutral']);
                    } else {
                      setSelectedSentiments(selectedSentiments.filter(s => s !== 'neutral'));
                    }
                  }}
                >
                  中性
                </Checkbox>
                <Checkbox 
                  checked={selectedSentiments.includes('negative')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSentiments([...selectedSentiments, 'negative']);
                    } else {
                      setSelectedSentiments(selectedSentiments.filter(s => s !== 'negative'));
                    }
                  }}
                >
                  负面
                </Checkbox>
              </Space>
            </div>
          </Space>
        </Modal>
      </div>
    );
  } catch (error) {
    console.error('默认表格渲染错误:', error);
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, width: '100%', color: '#999' }}>
        表格渲染失败
      </div>
    );
  }
});

TrendAnalysis.displayName = 'TrendAnalysis';

export default TrendAnalysis;