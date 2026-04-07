import React, { useEffect, useState } from 'react'
import { Card, Typography, Divider, List, Tag, Space, Button, Row, Col, Avatar, Descriptions, Badge, Tooltip as AntdTooltip } from 'antd'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend } from 'recharts'
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, ShareAltOutlined, CopyOutlined, AlertOutlined, ClockCircleOutlined, LinkOutlined, EyeOutlined, LikeOutlined, MessageOutlined, RetweetOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchOpinionDetail, selectSelectedOpinion, selectOpinionLoading } from '../store/features/opinionSlice'

const { Title, Text, Paragraph } = Typography
const { Item } = Descriptions

interface OpinionDetail {
  id: string
  content: string
  source: string
  source_platform: string
  publish_time: string
  crawl_time: string
  sentiment: number
  sentiment_type: 'positive' | 'negative' | 'neutral'
  keywords: string[]
  url?: string
  views: number
  likes: number
  comments: number
  shares: number
  heat_score: number
  is_sensitive: boolean
  sensitive_level: number
  location?: string
  user_info?: {
    id: string
    name: string
    avatar?: string
    verified?: boolean
    bio?: string
    followers?: number
    following?: number
  }
  raw_data?: Record<string, any>
  related_opinions?: {
    id: string
    content: string
    publish_time: string
  }[]
  analysis?: {
    sentiment_details: Record<string, number>
    keyword_analysis: Record<string, number>
    topic_classification: string[]
  }
  comments?: {
    id: string
    content: string
    user_name: string
    user_avatar?: string
    publish_time: string
    likes: number
    sentiment_type: 'positive' | 'negative' | 'neutral'
  }[]
}

const OpinionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const opinionDetail = useSelector(selectSelectedOpinion)
  const loading = useSelector(selectOpinionLoading)

  // 加载舆情详情数据
  useEffect(() => {
    if (id) {
      dispatch(fetchOpinionDetail({ id }))
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

  // 删除舆情
  const handleDelete = () => {
    // 实际项目中应该调用API删除舆情数据
    console.log('删除舆情', id)
    navigate('/opinion/list')
  }

  // 分享舆情
  const handleShare = () => {
    // 实际项目中应该实现分享功能
    console.log('分享舆情', id)
  }

  // 查看相关舆情
  const handleViewRelatedOpinion = (relatedId: string) => {
    navigate(`/opinion/detail/${relatedId}`)
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

  // 获取敏感内容标签
  const getSensitiveTag = (isSensitive: boolean, sensitiveLevel: number) => {
    if (!isSensitive) return null
    
    let color = 'orange'
    let text = '敏感'
    
    if (sensitiveLevel >= 8) {
      color = 'red'
      text = '高敏感'
    } else if (sensitiveLevel >= 5) {
      color = 'orange'
      text = '中敏感'
    }
    
    return (
      <AntdTooltip title={`敏感级别: ${sensitiveLevel}`}>
        <Tag color={color} icon={<AlertOutlined />}>{text}</Tag>
      </AntdTooltip>
    )
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Title level={4} className="mb-6">舆情详情</Title>
        <Card loading={true} className="h-64" />
      </div>
    )
  }

  // 生成模拟的互动数据趋势
  const [interactionTrendData, setInteractionTrendData] = useState<any[]>([])
  
  useEffect(() => {
    // 生成过去7天的互动数据趋势
    const generateInteractionTrendData = () => {
      const data = []
      const today = new Date()
      
      // 为过去7天生成数据
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        // 生成基于原始数据的波动值
        const baseViewCount = opinionDetail?.views || 1000
        const baseLikeCount = opinionDetail?.likes || 200
        const baseCommentCount = opinionDetail?.comments || 50
        const baseShareCount = opinionDetail?.shares || 30
        
        data.push({
          date: date.toLocaleDateString(),
          viewCount: Math.floor(baseViewCount * (0.8 + Math.random() * 0.4)),
          likeCount: Math.floor(baseLikeCount * (0.8 + Math.random() * 0.4)),
          commentCount: Math.floor(baseCommentCount * (0.8 + Math.random() * 0.4)),
          shareCount: Math.floor(baseShareCount * (0.8 + Math.random() * 0.4))
        })
      }
      return data
    }
    
    setInteractionTrendData(generateInteractionTrendData())
  }, [opinionDetail])
  
  // 情感分布数据
  const sentimentData = [
    { name: '正面', value: opinionDetail?.sentiment || 60, color: '#52c41a' },
    { name: '负面', value: 100 - (opinionDetail?.sentiment || 60), color: '#ff4d4f' }
  ]
  
  // 渲染情感分布饼图
  const renderSentimentPieChart = () => {
    return (
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={sentimentData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={60}
            fill="#8884d8"
            dataKey="value"
            startAngle={90}
            endAngle={-270}
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
  
  // 渲染互动数据趋势图
  const renderInteractionTrendChart = () => {
    return (
      <ResponsiveContainer width="100%" height={250}>
        <BarChart
          data={interactionTrendData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="viewCount" name="浏览量" fill="#8884d8" />
          <Bar dataKey="likeCount" name="点赞数" fill="#ff7875" />
          <Bar dataKey="commentCount" name="评论数" fill="#1890ff" />
          <Bar dataKey="shareCount" name="分享数" fill="#52c41a" />
        </BarChart>
      </ResponsiveContainer>
    )
  }
  if (!opinionDetail) {
    return (
      <div className="error-container">
        <Title level={4} className="mb-6">舆情详情</Title>
        <Card>
          <Text type="danger">未找到该舆情数据</Text>
          <Button type="primary" onClick={handleBack} className="mt-4">返回列表</Button>
        </Card>
      </div>
    )
  }

  const { 
    content, source_platform, publish_time, sentiment_type, keywords, 
    url, views, likes, comments: commentCount, shares, heat_score, 
    is_sensitive, sensitive_level, location, user_info, related_opinions, 
    analysis, comments 
  } = opinionDetail

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <Title level={4}>舆情详情</Title>
        <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>返回列表</Button>
      </div>

      {/* 主要内容卡片 */}
      <Card className="mb-6">
        {/* 用户信息和发布时间 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Avatar src={user_info?.avatar} alt={user_info?.name}>
              {user_info?.name?.charAt(0) || 'U'}
            </Avatar>
            <div className="ml-3">
              <div className="flex items-center">
                <Text strong>{user_info?.name}</Text>
                {user_info?.verified && (
                  <Badge status="success" className="ml-2" />
                )}
              </div>
              <Text type="secondary" className="text-sm">{source_platform}</Text>
            </div>
          </div>
          <Text type="secondary" className="text-sm">
            <ClockCircleOutlined className="mr-1" />
            {new Date(publish_time).toLocaleString()}
          </Text>
        </div>

        {/* 舆情内容 */}
        <Paragraph className="text-lg mb-6 whitespace-pre-wrap">{content}</Paragraph>

        {/* 来源链接 */}
        {url && (
          <div className="mb-6">
            <Text type="secondary">来源链接：</Text>
            <a href={url} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-600 hover:underline">
              {url}
            </a>
          </div>
        )}

        {/* 互动数据 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex space-x-6">
            <div className="flex items-center">
              <EyeOutlined className="mr-1" />
              <Text>{views} 浏览</Text>
            </div>
            <div className="flex items-center">
              <LikeOutlined className="mr-1" />
              <Text>{likes} 点赞</Text>
            </div>
            <div className="flex items-center">
              <MessageOutlined className="mr-1" />
              <Text>{commentCount} 评论</Text>
            </div>
            <div className="flex items-center">
              <RetweetOutlined className="mr-1" />
              <Text>{shares} 分享</Text>
            </div>
          </div>
        </div>

        {/* 标签和评分 */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          {getSentimentTag(sentiment_type)}
          {getSensitiveTag(is_sensitive, sensitive_level)}
          {location && <Tag color="purple">{location}</Tag>}
          <Tag color="geekblue">热度: {heat_score}</Tag>
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

        {/* 操作按钮 */}
        <div className="flex justify-end space-x-2">
          <AntdTooltip title="复制内容">
            <Button icon={<CopyOutlined />} onClick={() => handleCopy(content)} />
          </AntdTooltip>
          <AntdTooltip title="分享">
            <Button icon={<ShareAltOutlined />} onClick={handleShare} />
          </AntdTooltip>
          <AntdTooltip title="编辑">
            <Button type="primary" icon={<EditOutlined />} />
          </AntdTooltip>
          <AntdTooltip title="删除">
            <Button danger icon={<DeleteOutlined />} onClick={handleDelete} />
          </AntdTooltip>
        </div>
      </Card>

      {/* 数据统计和分析 */}
      {analysis && (
        <Card title="数据分析" className="mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold mb-4">情感分布</h4>
              {renderSentimentPieChart()}
            </div>
            <div>
              <Descriptions bordered>
                <Item label="情感分析">
                  <div className="space-y-2">
                    {Object.entries(analysis.sentiment_details).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <Text>{key}</Text>
                        <div className="w-32 bg-gray-200 rounded-full h-2.5">
                          <div 
                            className="bg-blue-600 h-2.5 rounded-full" 
                            style={{ width: `${value}%` }}
                          ></div>
                        </div>
                        <Text strong>{value}%</Text>
                      </div>
                    ))}
                  </div>
                </Item>
                <Item label="关键词分析">
                  <Space wrap>
                    {Object.entries(analysis.keyword_analysis).map(([key, value]) => (
                      <Tag key={key} color="blue">{key}({value})</Tag>
                    ))}
                  </Space>
                </Item>
                <Item label="主题分类">
                  <Space wrap>
                    {analysis.topic_classification.map((topic, index) => (
                      <Tag key={index} color="green">{topic}</Tag>
                    ))}
                  </Space>
                </Item>
              </Descriptions>
            </div>
          </div>
        </Card>
      )}

      {/* 互动数据趋势图表 */}
      <Card title="互动数据趋势" className="mb-6">
        {renderInteractionTrendChart()}
      </Card>

      {/* 用户信息详情 */}
      {user_info && (
        <Card title="发布者信息" className="mb-6">
          <Descriptions>
            <Item label="用户名">{user_info.name}</Item>
            <Item label="用户ID">{user_info.id}</Item>
            {user_info.bio && <Item label="简介">{user_info.bio}</Item>}
            {user_info.followers !== undefined && <Item label="粉丝数">{user_info.followers.toLocaleString()}</Item>}
            {user_info.following !== undefined && <Item label="关注数">{user_info.following.toLocaleString()}</Item>}
          </Descriptions>
        </Card>
      )}

      {/* 相关舆情 */}
      {related_opinions && related_opinions.length > 0 && (
        <Card title="相关舆情" className="mb-6">
          <List
            itemLayout="horizontal"
            dataSource={related_opinions}
            renderItem={(item) => (
              <List.Item
                key={item.id}
                actions={[
                  <Text type="secondary" key="time">
                    {new Date(item.publish_time).toLocaleString()}
                  </Text>
                ]}
                onClick={() => handleViewRelatedOpinion(item.id)}
                className="cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <List.Item.Meta
                  title={
                    <Text ellipsis={{ tooltip: item.content }} className="block max-w-[80%]">
                      {item.content}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* 评论列表 */}
      {comments && comments.length > 0 && (
        <Card title="评论列表" className="mb-6">
          <List
            itemLayout="horizontal"
            dataSource={comments}
            renderItem={(item) => (
              <List.Item
                key={item.id}
                avatar={<Avatar src={item.user_avatar}>{item.user_name.charAt(0)}</Avatar>}
                actions={[
                  getSentimentTag(item.sentiment_type),
                  <Text key="likes">{item.likes} 点赞</Text>,
                  <Text type="secondary" key="time">
                    {new Date(item.publish_time).toLocaleString()}
                  </Text>
                ]}
              >
                <List.Item.Meta
                  title={item.user_name}
                  description={item.content}
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  )
}

export default OpinionDetail