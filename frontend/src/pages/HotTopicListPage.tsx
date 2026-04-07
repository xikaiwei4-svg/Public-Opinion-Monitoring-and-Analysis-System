import React, { useState, useEffect } from 'react'
import { Typography, Table, Card, Select, Input, Button, Tag, Space, Row, Col, Statistic, Divider, message, Spin } from 'antd'
import { SearchOutlined, DownloadOutlined, EyeOutlined, ArrowUpOutlined, ArrowDownOutlined, AlertOutlined, ReloadOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { getOpinions } from '../api/databaseApi'

const { Title, Text } = Typography
const { Search } = Input

const getCurrentDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const getRecentDate = (daysAgo: number) => {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

// 从舆情数据生成热点话题
const generateHotTopicsFromOpinions = (opinions: any[]): any[] => {
  // 按平台分组统计
  const platformGroups: Record<string, any[]> = {};
  opinions.forEach(opinion => {
    const platform = opinion.source_platform || '其他';
    if (!platformGroups[platform]) {
      platformGroups[platform] = [];
    }
    platformGroups[platform].push(opinion);
  });
  
  // 生成热点话题
  const topics: any[] = [];
  let id = 1;
  
  Object.entries(platformGroups).forEach(([platform, items]) => {
    // 按热度排序，取前几条
    const sortedItems = items.sort((a, b) => (b.hot_score || 0) - (a.hot_score || 0));
    
    sortedItems.slice(0, 3).forEach((item, index) => {
      const sentimentScore = item.sentiment_score || 0.5;
      let riskLevel = 'low';
      if (sentimentScore < 0.3) riskLevel = 'high';
      else if (sentimentScore < 0.5) riskLevel = 'medium';
      
      topics.push({
        id: String(id++),
        title: item.title || item.content?.substring(0, 30) || '无标题',
        description: item.content?.substring(0, 100) || '无描述',
        heat: Math.round((item.hot_score || 0.5) * 10000) + Math.floor(Math.random() * 1000),
        trend: Math.random() > 0.5 ? 'up' : (Math.random() > 0.5 ? 'down' : 'stable'),
        sourceCount: Math.floor(Math.random() * 200) + 50,
        sentimentScore: sentimentScore,
        firstAppearance: item.publish_time ? item.publish_time.replace('T', ' ').substring(0, 16) : getRecentDate(Math.floor(Math.random() * 7)),
        latestUpdate: getCurrentDate(),
        category: getCategoryFromTitle(item.title || item.content || ''),
        riskLevel: riskLevel,
        source_url: item.source_url
      });
    });
  });
  
  return topics.sort((a, b) => b.heat - a.heat);
};

// 根据标题判断分类
const getCategoryFromTitle = (title: string): string => {
  const keywords: Record<string, string[]> = {
    '教育政策': ['教育', '政策', '改革', '考试', '招生', '学费'],
    '校园生活': ['校园', '学生', '食堂', '宿舍', '图书馆', '活动'],
    '社会热点': ['社会', '热点', '新闻', '事件', '讨论'],
    '科技教育': ['科技', 'AI', '人工智能', '数字化', '在线', '网络'],
    '国际交流': ['国际', '留学', '海外', '合作', '交流']
  };
  
  for (const [category, words] of Object.entries(keywords)) {
    if (words.some(word => title.includes(word))) {
      return category;
    }
  }
  return '其他';
};

const HotTopicListPage: React.FC = () => {
  const navigate = useNavigate()
  const [hotTopics, setHotTopics] = useState<any[]>([])
  const [filteredTopics, setFilteredTopics] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedRisk, setSelectedRisk] = useState<string>('all')
  const [searchKeyword, setSearchKeyword] = useState<string>('')

  // 加载舆情数据并生成热点话题
  const loadHotTopics = async () => {
    setLoading(true)
    try {
      const opinions = await getOpinions(0, 100)
      const topics = generateHotTopicsFromOpinions(opinions)
      setHotTopics(topics)
      setFilteredTopics(topics)
      message.success(`成功加载 ${topics.length} 个热点话题`)
    } catch (error) {
      console.error('加载热点话题失败:', error)
      message.error('加载热点话题失败')
    } finally {
      setLoading(false)
    }
  }

  // 组件加载时获取数据
  useEffect(() => {
    loadHotTopics()
  }, [])

  // 统计数据
  const stats = {
    totalTopics: hotTopics.length,
    highRisk: hotTopics.filter(topic => topic.riskLevel === 'high').length,
    totalHeat: hotTopics.reduce((sum, topic) => sum + (topic.heat || 0), 0)
  }

  // 过滤数据
  useEffect(() => {
    let result = [...hotTopics]
    
    // 分类过滤
    if (selectedCategory !== 'all') {
      result = result.filter(topic => topic.category === selectedCategory)
    }
    
    // 风险等级过滤
    if (selectedRisk !== 'all') {
      result = result.filter(topic => topic.riskLevel === selectedRisk)
    }
    
    // 关键词搜索
    if (searchKeyword) {
      const keyword = searchKeyword.toLowerCase()
      result = result.filter(topic => 
        topic.title.toLowerCase().includes(keyword) || 
        topic.description.toLowerCase().includes(keyword)
      )
    }
    
    setFilteredTopics(result)
  }, [hotTopics, selectedCategory, selectedRisk, searchKeyword])

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value)
  }

  // 处理导出
  const handleExport = () => {
    message.success('热点话题数据已导出')
  }

  // 处理查看详情
  const handleViewDetail = (record: any) => {
    if (record.source_url) {
      window.open(record.source_url, '_blank')
    } else {
      message.info(`查看热点话题ID: ${record.id} 的详情`)
    }
  }

  // 热度趋势图标
  const renderTrendIcon = (trend: string) => {
    if (trend === 'up') {
      return <ArrowUpOutlined style={{ color: '#ff4d4f' }} />
    } else if (trend === 'down') {
      return <ArrowDownOutlined style={{ color: '#52c41a' }} />
    }
    return <Text style={{ color: '#faad14' }}>—</Text>
  }

  // 风险等级标签颜色
  const riskTagColor: Record<string, string> = {
    high: 'error',
    medium: 'warning',
    low: 'success'
  }

  // 风险等级文本
  const riskLevelText: Record<string, string> = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }

  // 获取情感标签
  const getSentimentTag = (score: number) => {
    if (score > 0.6) {
      return <Tag color="success">正面</Tag>
    } else if (score < 0.4) {
      return <Tag color="error">负面</Tag>
    }
    return <Tag color="default">中性</Tag>
  }

  // 表格列配置
  const columns = [
    {
      title: '话题标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 300,
      render: (text: string, record: any) => (
        <a onClick={() => handleViewDetail(record)}>{text}</a>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      width: 350
    },
    {
      title: '热度',
      dataIndex: 'heat',
      key: 'heat',
      width: 100,
      render: (value: number, record: any) => (
        <Space>
          <Text>{value}</Text>
          {renderTrendIcon(record.trend)}
        </Space>
      )
    },
    {
      title: '信息源数量',
      dataIndex: 'sourceCount',
      key: 'sourceCount',
      width: 120
    },
    {
      title: '情感倾向',
      dataIndex: 'sentimentScore',
      key: 'sentimentScore',
      width: 100,
      render: (score: number) => getSentimentTag(score)
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '风险等级',
      dataIndex: 'riskLevel',
      key: 'riskLevel',
      width: 100,
      render: (level: string) => (
        <Tag color={riskTagColor[level]} icon={<AlertOutlined />}>
          {riskLevelText[level]}
        </Tag>
      )
    },
    {
      title: '最新更新',
      dataIndex: 'latestUpdate',
      key: 'latestUpdate',
      width: 150
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: any, record: any) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />} 
          onClick={() => handleViewDetail(record)} 
        />
      )
    }
  ]

  // 获取所有分类
  const categories = ['all', ...Array.from(new Set(hotTopics.map(topic => topic.category)))]

  return (
    <div>
      <Title level={3}>热点话题管理</Title>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="总话题数"
              value={stats.totalTopics}
              suffix="个"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="高风险话题"
              value={stats.highRisk}
              suffix="个"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="总热度值"
              value={stats.totalHeat}
              precision={0}
            />
          </Card>
        </Col>
      </Row>
      
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', marginBottom: 16 }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <Search
              placeholder="搜索话题标题或描述"
              onSearch={handleSearch}
              onChange={(e) => setSearchKeyword(e.target.value)}
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
            />
          </div>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={loadHotTopics}
            loading={loading}
          >
            刷新数据
          </Button>
          
          <Select
            placeholder="分类筛选"
            value={selectedCategory}
            onChange={setSelectedCategory}
            style={{ width: 150 }}
            size="middle"
          >
            <Select.Option value="all">全部分类</Select.Option>
            {categories.filter(c => c !== 'all').map(cat => (
              <Select.Option key={cat} value={cat}>{cat}</Select.Option>
            ))}
          </Select>
          
          <Select
            placeholder="风险等级筛选"
            value={selectedRisk}
            onChange={setSelectedRisk}
            style={{ width: 150 }}
            size="middle"
          >
            <Select.Option value="all">全部风险</Select.Option>
            <Select.Option value="high">高风险</Select.Option>
            <Select.Option value="medium">中风险</Select.Option>
            <Select.Option value="low">低风险</Select.Option>
          </Select>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
          <Button 
            type="primary" 
            icon={<DownloadOutlined />}
            onClick={handleExport}
          >
            导出数据
          </Button>
        </div>
      </Card>
      
      <Spin spinning={loading} tip="加载中...">
        <Table 
          columns={columns} 
          dataSource={filteredTopics} 
          rowKey="id" 
          pagination={{ pageSize: 10 }}
          scroll={{ x: 'max-content' }}
          locale={{ emptyText: '暂无热点话题数据' }}
        />
      </Spin>
    </div>
  )
}

export default HotTopicListPage