import React, { useState, useEffect } from 'react'
import { Card, Typography, DatePicker, Select, Row, Col, Space, Divider, Button, Statistic, Tag } from 'antd'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { ArrowLeftOutlined, BarChartOutlined, LineChartOutlined, PieChartOutlined, ArrowUpOutlined, CalendarOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchHotTopicTrend, selectSelectedTopic, selectHotTopicLoading } from '../store/features/hotTopicSlice'

const { Title, Text } = Typography
const { RangePicker } = DatePicker
const { Option } = Select

interface TrendData {
  time: string
  hot_value: number
  opinion_count: number
  sentiment_distribution: {
    positive: number
    negative: number
    neutral: number
  }
  platform_distribution: {
    [key: string]: number
  }
}

const HotTopicTrend: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const selectedTopic = useSelector(selectSelectedTopic)
  const hotTopicTrend = selectedTopic?.trend_data || null
  const loading = useSelector(selectHotTopicLoading)
  const [dateRange, setDateRange] = useState<any>(null)
  const [chartType, setChartType] = useState<'line' | 'bar'>('line')
  const [dataType, setDataType] = useState<'hot_value' | 'opinion_count'>('hot_value')

  // 加载趋势数据
  useEffect(() => {
    if (id) {
      dispatch(fetchHotTopicTrend({ id }))
    }
  }, [dispatch, id])

  // 返回上一页
  const handleBack = () => {
    navigate(-1)
  }

  // 日期范围变化处理
  const handleDateRangeChange = (dates: any) => {
    setDateRange(dates)
    // 实际项目中应该根据日期范围筛选数据
    console.log('日期范围变化', dates)
  }

  // 获取趋势状态对应的图标和颜色
  const getTrendStatus = (status: string) => {
    switch (status) {
      case 'rising':
        return <Tag color="red" icon={<ArrowUpOutlined />}>上升</Tag>
      case 'stable':
        return <Tag color="blue">稳定</Tag>
      case 'falling':
        return <Tag color="green">下降</Tag>
      default:
        return <Tag>未知</Tag>
    }
  }

  // 渲染趋势图表
  const renderChart = () => {
    const trendData = hotTopicTrend?.trend_data || [];
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={trendData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone" 
            dataKey="hot_value" 
            name="热度值" 
            stroke="#ff7875" 
            activeDot={{ r: 8 }} 
          />
          <Line
            yAxisId="right"
            type="monotone" 
            dataKey="opinion_count" 
            name="舆情数量" 
            stroke="#1890ff" 
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  // 渲染情感分布饼图
  const renderSentimentPieChart = () => {
    const trendData = hotTopicTrend?.trend_data || [];
    
    // 从趋势数据中聚合情感分布
    const sentimentData = [
      { name: '正面', value: trendData.reduce((sum, item) => sum + (item.sentiment_distribution?.positive || 0), 0), color: '#52c41a' },
      { name: '中性', value: trendData.reduce((sum, item) => sum + (item.sentiment_distribution?.neutral || 0), 0), color: '#faad14' },
      { name: '负面', value: trendData.reduce((sum, item) => sum + (item.sentiment_distribution?.negative || 0), 0), color: '#ff4d4f' }
    ]

    return (
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={sentimentData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {sentimentData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <RechartsTooltip />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  // 渲染平台分布饼图
  const renderPlatformPieChart = () => {
    const trendData = hotTopicTrend?.trend_data || [];
    
    // 从趋势数据中聚合平台分布
    const platformData = [
      { name: '微博', value: trendData.reduce((sum, item) => sum + (item.platform_distribution?.weibo || 0), 0), color: '#e6162d' },
      { name: '微信', value: trendData.reduce((sum, item) => sum + (item.platform_distribution?.wechat || 0), 0), color: '#07c160' },
      { name: '抖音', value: trendData.reduce((sum, item) => sum + (item.platform_distribution?.douyin || 0), 0), color: '#000000' },
      { name: '知乎', value: trendData.reduce((sum, item) => sum + (item.platform_distribution?.zhihu || 0), 0), color: '#0f88eb' },
      { name: '其他', value: trendData.reduce((sum, item) => sum + (item.platform_distribution?.other || 0), 0), color: '#8c8c8c' }
    ].filter(item => item.value > 0)

    return (
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={platformData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {platformData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <RechartsTooltip />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Title level={4} className="mb-6">话题趋势分析</Title>
        <Card loading={true} className="h-64" />
      </div>
    )
  }

  if (!hotTopicTrend) {
    return (
      <div className="error-container">
        <Title level={4} className="mb-6">话题趋势分析</Title>
        <Card>
          <Text type="danger">未找到该话题的趋势数据</Text>
          <Button type="primary" onClick={handleBack} className="mt-4">返回详情</Button>
        </Card>
      </div>
    )
  }

  const { topic_name, trend_data, overall_trend_status, sentiment_summary, platform_summary } = hotTopicTrend

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <Title level={4} className="mb-0">话题趋势分析</Title>
        <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>返回详情</Button>
      </div>

      {/* 话题名称和趋势状态 */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <h2 className="text-2xl font-bold m-0">{topic_name}</h2>
          <div className="flex items-center">
            <Text type="secondary" className="mr-2">整体趋势：</Text>
            {getTrendStatus(overall_trend_status)}
          </div>
        </div>

        {/* 筛选条件 */}
        <Row gutter={16} className="flex items-center">
          <Col xs={24} sm={12} md={6}>
            <Space>
              <Text>日期范围：</Text>
              <RangePicker onChange={handleDateRangeChange} />
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space>
              <Text>图表类型：</Text>
              <Select 
                value={chartType} 
                onChange={(value: 'line' | 'bar') => setChartType(value)}
                style={{ width: 120 }}
              >
                <Option value="line">折线图</Option>
                <Option value="bar">柱状图</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space>
              <Text>数据类型：</Text>
              <Select 
                value={dataType} 
                onChange={(value: 'hot_value' | 'opinion_count') => setDataType(value)}
                style={{ width: 120 }}
              >
                <Option value="hot_value">热度值</Option>
                <Option value="opinion_count">舆情数量</Option>
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Button type="primary" className="w-full sm:w-auto">
              导出数据
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 趋势图表 */}
      <Card title="趋势图表" className="mb-6">
        {renderChart()}
      </Card>

      {/* 关键指标 */}
      <Row gutter={16} className="mb-6">
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic 
              title="最高热度值" 
              value={trend_data ? Math.max(...trend_data.map(item => item.hot_value)) : 0} 
              suffix="分"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic 
              title="总舆情数量" 
              value={trend_data ? trend_data.reduce((sum, item) => sum + item.opinion_count, 0) : 0} 
              suffix="条"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic 
              title="平均热度值" 
              value={trend_data ? Math.round(trend_data.reduce((sum, item) => sum + item.hot_value, 0) / trend_data.length) : 0} 
              suffix="分"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic 
              title="数据跨度" 
              value={trend_data && trend_data.length > 1 ? `${new Date(trend_data[0].time).toLocaleDateString()} - ${new Date(trend_data[trend_data.length - 1].time).toLocaleDateString()}` : '暂无数据'} 
              valueStyle={{ fontSize: '14px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 情感分布和平台分布 */}
      <Row gutter={16} className="mb-6">
        <Col xs={24} md={12}>
          <Card title="情感分布" extra={<PieChartOutlined />}>
            {renderSentimentPieChart()}
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center">
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#52c41a', marginRight: '8px' }}></div>
                  <Text>正面情绪</Text>
                </div>
                <Text>{sentiment_summary?.positive_percentage || 0}%</Text>
              </div>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center">
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#1890ff', marginRight: '8px' }}></div>
                  <Text>中性情绪</Text>
                </div>
                <Text>{sentiment_summary?.neutral_percentage || 0}%</Text>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div style={{ width: '12px', height: '12px', backgroundColor: '#ff4d4f', marginRight: '8px' }}></div>
                  <Text>负面情绪</Text>
                </div>
                <Text>{sentiment_summary?.negative_percentage || 0}%</Text>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="平台分布" extra={<PieChartOutlined />}>
            {renderPlatformPieChart()}
            <div className="mt-4">
              {platform_summary && Object.entries(platform_summary).map(([platform, count], index) => (
                <div key={index} className="flex justify-between items-center mb-2">
                  <div className="flex items-center">
                    <div style={{ 
                      width: '12px', 
                      height: '12px', 
                      backgroundColor: index % 5 === 0 ? '#1890ff' : index % 5 === 1 ? '#52c41a' : index % 5 === 2 ? '#faad14' : index % 5 === 3 ? '#f5222d' : '#722ed1', 
                      marginRight: '8px' 
                    }}></div>
                    <Text>{platform}</Text>
                  </div>
                  <Text>{count}条</Text>
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 趋势分析总结 */}
      <Card title="趋势分析总结" className="mb-6">
        <div className="mb-4">
          <Text strong className="block mb-2">整体趋势分析：</Text>
          <Text>
            根据数据显示，该话题呈现{overall_trend_status === 'rising' ? '上升' : overall_trend_status === 'falling' ? '下降' : '稳定'}趋势。
            热度最高值出现在{trend_data && trend_data.length > 0 ? new Date(trend_data.reduce((max, item) => item.hot_value > max.hot_value ? item : max, trend_data[0]).time).toLocaleString() : '暂无数据'}，
            达到{trend_data ? Math.max(...trend_data.map(item => item.hot_value)) : 0}分。
          </Text>
        </div>
        
        <div className="mb-4">
          <Text strong className="block mb-2">情感倾向分析：</Text>
          <Text>
            该话题的整体情感倾向以{sentiment_summary?.dominant_sentiment || '中性'}为主，
            正面情绪占比{sentiment_summary?.positive_percentage || 0}%，
            负面情绪占比{sentiment_summary?.negative_percentage || 0}%，
            中性情绪占比{sentiment_summary?.neutral_percentage || 0}%。
          </Text>
        </div>
        
        <div className="mb-4">
          <Text strong className="block mb-2">平台分布分析：</Text>
          <Text>
            该话题主要分布在{platform_summary && Object.keys(platform_summary).length > 0 ? Object.keys(platform_summary).join('、') : '各平台'}，
            其中{platform_summary && Object.entries(platform_summary).length > 0 ? 
              Object.entries(platform_summary).reduce((a, b) => a[1] > b[1] ? a : b)[0] 
            : '暂无数据'}平台的相关舆情数量最多。
          </Text>
        </div>
      </Card>

      {/* 数据表格 */}
      <Card title="趋势数据明细" className="mb-6">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-4 py-2 text-left">时间</th>
                <th className="border border-gray-300 px-4 py-2 text-left">热度值</th>
                <th className="border border-gray-300 px-4 py-2 text-left">舆情数量</th>
                <th className="border border-gray-300 px-4 py-2 text-left">正面情绪</th>
                <th className="border border-gray-300 px-4 py-2 text-left">中性情绪</th>
                <th className="border border-gray-300 px-4 py-2 text-left">负面情绪</th>
              </tr>
            </thead>
            <tbody>
              {trend_data ? (
                trend_data.map((item, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="border border-gray-300 px-4 py-2">{new Date(item.time).toLocaleString()}</td>
                    <td className="border border-gray-300 px-4 py-2">{item.hot_value}</td>
                    <td className="border border-gray-300 px-4 py-2">{item.opinion_count}</td>
                    <td className="border border-gray-300 px-4 py-2">{item.sentiment_distribution.positive}</td>
                    <td className="border border-gray-300 px-4 py-2">{item.sentiment_distribution.neutral}</td>
                    <td className="border border-gray-300 px-4 py-2">{item.sentiment_distribution.negative}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="border border-gray-300 px-4 py-4 text-center">暂无数据</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

export default HotTopicTrend