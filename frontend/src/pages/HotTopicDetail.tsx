import React, { useState, useEffect } from 'react'
import { Card, Typography, Divider, List, Tag, Space, Button, Row, Col, Avatar, Descriptions, Badge, Tooltip as AntdTooltip, Statistic, Progress, Timeline, Collapse } from 'antd'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, ShareAltOutlined, CopyOutlined, AlertOutlined, ClockCircleOutlined, LinkOutlined, BarChartOutlined, ArrowUpOutlined, UsersOutlined, CalendarOutlined, MessageOutlined, EyeOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchHotTopicDetail, selectSelectedTopic, selectHotTopicLoading } from '../store/features/hotTopicSlice'

const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse
const { Item } = Descriptions

interface HotTopicDetail {
  id: string
  title: string
  description: string
  keywords: string[]
  related_opinions_count: number
  start_time: string
  end_time: string
  peak_time?: string
  hot_value: number
  trend_status: 'rising' | 'stable' | 'falling'
  platforms: string[]
  sentiment_distribution: {
    positive: number
    negative: number
    neutral: number
  }
  topic_category: string
  is_official?: boolean
  source_link?: string
  influencers?: {
    id: string
    name: string
    platform: string
    influence_score: number
    avatar?: string
    description?: string
  }[]
  trend_data?: {
    time: string
    hot_value: number
    opinion_count: number
  }[]
  key_opinions?: {
    id: string
    content: string
    publish_time: string
    source_platform: string
    user_name: string
    sentiment_type: 'positive' | 'negative' | 'neutral'
    likes: number
    comments: number
  }[]
  analysis?: {
    summary: string
    development_stages: {
      stage: string
      description: string
      time: string
    }[]
    influence_factors: string[]
    predicted_trend: 'rising' | 'stable' | 'falling'
  }
}

const HotTopicDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const hotTopicDetail = useSelector(selectSelectedTopic)
  const loading = useSelector(selectHotTopicLoading)

  // 加载热点话题详情数据
  useEffect(() => {
    if (id) {
      dispatch(fetchHotTopicDetail({ id }))
    }
  }, [dispatch, id])

  // 返回上一页
  const handleBack = () => {
    navigate(-1)
  }

  // 复制内容
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    // 实际项目中应该有一个提示组件
    console.log('已复制到剪贴板')
  }

  // 删除热点话题
  const handleDelete = () => {
    // 实际项目中应该调用API删除热点话题数据
    console.log('删除热点话题', id)
    navigate('/hot-topic/list')
  }

  // 分享热点话题
  const handleShare = () => {
    // 实际项目中应该实现分享功能
    console.log('分享热点话题', id)
  }

  // 查看相关舆情
  const handleViewOpinion = (opinionId: string) => {
    navigate(`/opinion/detail/${opinionId}`)
  }

  // 查看话题趋势
  const handleViewTrend = () => {
    navigate(`/hot-topic/trend/${id}`)
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

  // 获取分类对应的标签
  const getCategoryTag = (category: string) => {
    const categoryMap: Record<string, { label: string; color: string }> = {
      'education_policy': { label: '教育政策', color: 'purple' },
      'campus_life': { label: '校园生活', color: 'cyan' },
      'academic_activity': { label: '学术活动', color: 'green' },
      'school_news': { label: '学校动态', color: 'orange' },
      'other': { label: '其他话题', color: 'default' }
    }
    
    const categoryInfo = categoryMap[category] || { label: category, color: 'default' }
    return <Tag color={categoryInfo.color}>{categoryInfo.label}</Tag>
  }

  // 获取情感类型对应的标签样式
  const getSentimentTag = (sentimentType: string) => {
    switch (sentimentType) {
      case 'positive':
        return <Tag color="green">正面</Tag>
      case 'negative':
        return <Tag color="red">负面</Tag>
      case 'neutral':
        return <Tag color="blue">中性</Tag>
      default:
        return <Tag>未知</Tag>
    }
  }

  // 渲染情感分布进度条
  const renderSentimentDistribution = (distribution: { positive: number; negative: number; neutral: number }) => {
    const { positive, negative, neutral } = distribution
    const total = positive + negative + neutral
    
    return (
      <Space direction="vertical" size="small" className="w-full">
        <div className="flex justify-between">
          <Text>正面</Text>
          <Text>{Math.round((positive / total) * 100)}%</Text>
        </div>
        <Progress percent={(positive / total) * 100} strokeColor="#52c41a" />
        
        <div className="flex justify-between">
          <Text>中性</Text>
          <Text>{Math.round((neutral / total) * 100)}%</Text>
        </div>
        <Progress percent={(neutral / total) * 100} strokeColor="#1890ff" />
        
        <div className="flex justify-between">
          <Text>负面</Text>
          <Text>{Math.round((negative / total) * 100)}%</Text>
        </div>
        <Progress percent={(negative / total) * 100} strokeColor="#ff4d4f" />
      </Space>
    )
  }

  // 生成模拟的趋势数据
  const [mockTrendData, setMockTrendData] = useState<any[]>([])
  
  useEffect(() => {
    // 生成过去7天的趋势数据
    const generateMockTrendData = () => {
      const data = []
      const today = new Date()
      
      // 为过去7天生成数据
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        // 根据原始热度值生成波动的数据
        const baseHotValue = hotTopicDetail?.hot_value || 80
        const variation = Math.floor(Math.random() * 20) - 10 // -10 到 10 的波动
        const hotValue = Math.max(1, baseHotValue + variation)
        
        // 根据热度值生成舆情数量
        const opinionCount = Math.floor(hotValue * (Math.random() * 2 + 8)) // 热度值的 8-10 倍
        
        data.push({
          date: date.toLocaleDateString(),
          hotValue,
          opinionCount
        })
      }
      return data
    }
    
    // 当API数据未返回时使用模拟数据
    if (!hotTopicDetail?.trend_data || hotTopicDetail.trend_data.length === 0) {
      setMockTrendData(generateMockTrendData())
    } else {
      setMockTrendData(hotTopicDetail.trend_data.map((item: any) => ({
        date: new Date(item.time).toLocaleDateString(),
        hotValue: item.hot_value,
        opinionCount: item.opinion_count
      })))
    }
  }, [hotTopicDetail])
  
  // 渲染趋势图表
  const renderTrendChart = () => {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={mockTrendData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorHotValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff7875" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ff7875" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorOpinionCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <CartesianGrid strokeDasharray="3 3" />
          <RechartsTooltip />
          <Legend />
          <Area
            yAxisId="left"
            type="monotone" 
            dataKey="hotValue" 
            name="热度值" 
            stroke="#ff7875" 
            fillOpacity={1} 
            fill="url(#colorHotValue)" 
          />
          <Area
            yAxisId="right"
            type="monotone" 
            dataKey="opinionCount" 
            name="舆情数量" 
            stroke="#1890ff" 
            fillOpacity={1} 
            fill="url(#colorOpinionCount)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Title level={4} className="mb-6">热点话题详情</Title>
        <Card loading={true} className="h-64" />
      </div>
    )
  }

  if (!hotTopicDetail) {
    return (
      <div className="error-container">
        <Title level={4} className="mb-6">热点话题详情</Title>
        <Card>
          <Text type="danger">未找到该热点话题数据</Text>
          <Button type="primary" onClick={handleBack} className="mt-4">返回列表</Button>
        </Card>
      </div>
    )
  }

  const { 
    title, description, keywords, related_opinions_count, start_time, end_time, peak_time, 
    hot_value, trend_status, platforms, sentiment_distribution, topic_category, 
    is_official, source_link, influencers, trend_data, key_opinions, analysis 
  } = hotTopicDetail

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Title level={4} className="mb-0">热点话题详情</Title>
          {is_official && <Badge status="processing" className="ml-3" />}
        </div>
        <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>返回列表</Button>
      </div>

      {/* 话题标题和基本信息卡片 */}
      <Card className="mb-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-3">{title}</h2>
          <Paragraph className="whitespace-pre-wrap">{description}</Paragraph>
        </div>

        {/* 关键指标 */}
        <Row gutter={16} className="mb-6">
          <Col xs={24} sm={12} md={6}>
            <Statistic title="热度值" value={hot_value} />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="相关舆情数" value={related_opinions_count} />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic 
              title="趋势状态" 
              value={getTrendStatus(trend_status).props.children} 
              valueStyle={{ color: trend_status === 'rising' ? '#f5222d' : trend_status === 'falling' ? '#52c41a' : '#1890ff' }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Statistic title="话题分类" value={getCategoryTag(topic_category).props.children} />
          </Col>
        </Row>

        {/* 标签和时间信息 */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          {getCategoryTag(topic_category)}
          {platforms.map((platform, index) => (
            <Tag key={index} color="geekblue">{platform}</Tag>
          ))}
          <Tag color="magenta">{new Date(start_time).toLocaleDateString()} - {new Date(end_time).toLocaleDateString()}</Tag>
          {peak_time && <Tag color="gold" icon={<ArrowUpOutlined />}>峰值: {new Date(peak_time).toLocaleString()}</Tag>}
        </div>

        {/* 关键词标签 */}
        <div className="mb-6">
          <Text type="secondary" className="mb-2 inline-block">关键词：</Text>
          <Space>
            {keywords.map((keyword, index) => (
              <Tag key={index}>{keyword}</Tag>
            ))}
          </Space>
        </div>

        {/* 来源链接 */}
        {source_link && (
          <div className="mb-6">
            <Text type="secondary">来源链接：</Text>
            <a href={source_link} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-600 hover:underline">
              {source_link}
            </a>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex justify-end space-x-2">
          <AntdTooltip title="复制内容">
            <Button icon={<CopyOutlined />} onClick={() => handleCopy(title + '\n' + description)} />
          </AntdTooltip>
          <AntdTooltip title="分享">
            <Button icon={<ShareAltOutlined />} onClick={handleShare} />
          </AntdTooltip>
          <AntdTooltip title="查看趋势">
            <Button type="primary" icon={<BarChartOutlined />} onClick={handleViewTrend} />
          </AntdTooltip>
          <AntdTooltip title="编辑">
            <Button type="primary" icon={<EditOutlined />} />
          </AntdTooltip>
          <AntdTooltip title="删除">
            <Button danger icon={<DeleteOutlined />} onClick={handleDelete} />
          </AntdTooltip>
        </div>
      </Card>

      {/* 趋势图表区域 */}
      <Card title="话题热度趋势" className="mb-6">
        {renderTrendChartPlaceholder()}
        <div className="mt-4 text-center">
          <Button type="link" onClick={handleViewTrend}>查看详细趋势分析</Button>
        </div>
      </Card>

      {/* 情感分析 */}
      <Card title="情感分析" className="mb-6">
        <Row gutter={16}>
          <Col xs={24} md={12}>
            {renderSentimentDistribution(sentiment_distribution)}
          </Col>
          <Col xs={24} md={12}>
            <div className="flex justify-around items-center h-full">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-500">{Math.round((sentiment_distribution.positive / (sentiment_distribution.positive + sentiment_distribution.negative + sentiment_distribution.neutral)) * 100)}%</div>
                <div>正面情绪</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-500">{Math.round((sentiment_distribution.neutral / (sentiment_distribution.positive + sentiment_distribution.negative + sentiment_distribution.neutral)) * 100)}%</div>
                <div>中性情绪</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-500">{Math.round((sentiment_distribution.negative / (sentiment_distribution.positive + sentiment_distribution.negative + sentiment_distribution.neutral)) * 100)}%</div>
                <div>负面情绪</div>
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 关键舆情 */}
      {key_opinions && key_opinions.length > 0 && (
        <Card title="关键舆情" className="mb-6">
          <List
            itemLayout="horizontal"
            dataSource={key_opinions}
            renderItem={(item) => (
              <List.Item
                key={item.id}
                actions={[
                  <Space key="stats">
                    <Text type="secondary"><EyeOutlined className="mr-1" />{item.likes}</Text>
                    <Text type="secondary"><MessageOutlined className="mr-1" />{item.comments}</Text>
                    <Text type="secondary">{new Date(item.publish_time).toLocaleString()}</Text>
                  </Space>
                ]}
                onClick={() => handleViewOpinion(item.id)}
                className="cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <List.Item.Meta
                  title={
                    <div className="flex items-center">
                      <Text ellipsis={{ tooltip: item.content }} className="block max-w-[70%]">
                        {item.content}
                      </Text>
                      {getSentimentTag(item.sentiment_type)}
                      <Tag color="geekblue" className="ml-2">{item.source_platform}</Tag>
                    </div>
                  }
                  description={
                    <div className="flex items-center">
                      <Text type="secondary">{item.user_name}</Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
          <div className="mt-4 text-center">
            <Button type="link">查看全部相关舆情</Button>
          </div>
        </Card>
      )}

      {/* 影响力人物 */}
      {influencers && influencers.length > 0 && (
        <Card title="影响力人物" className="mb-6">
          <List
            itemLayout="horizontal"
            dataSource={influencers}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar src={item.avatar}>{item.name.charAt(0)}</Avatar>}
                  title={
                    <div className="flex items-center">
                      <Text>{item.name}</Text>
                      <Tag color="blue" className="ml-2">{item.platform}</Tag>
                      <Tag color="orange">影响力: {item.influence_score}</Tag>
                    </div>
                  }
                  description={item.description}
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* 话题分析 */}
      {analysis && (
        <Card title="话题分析" className="mb-6">
          <Paragraph className="mb-6">{analysis.summary}</Paragraph>
          
          <Collapse defaultActiveKey={['1', '2', '3']}>
            <Panel header="发展阶段" key="1">
              <Timeline>
                {analysis.development_stages.map((stage, index) => (
                  <Timeline.Item key={index}>
                    <div>
                      <Text strong>{stage.stage}</Text>
                      <Text type="secondary" className="ml-2">{stage.time}</Text>
                    </div>
                    <Text>{stage.description}</Text>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Panel>
            
            <Panel header="影响因素" key="2">
              <List
                dataSource={analysis.influence_factors}
                renderItem={(factor, index) => (
                  <List.Item key={index}>
                    <span className="mr-2">•</span>
                    {factor}
                  </List.Item>
                )}
              />
            </Panel>
            
            <Panel header="预测趋势" key="3">
              <div className="flex items-center">
                <Text strong className="mr-2">预计趋势：</Text>
                {getTrendStatus(analysis.predicted_trend)}
              </div>
            </Panel>
          </Collapse>
        </Card>
      )}
    </div>
  )
}

export default HotTopicDetail