import React, { useState, useEffect } from 'react'
import { Typography, Table, Card, Select, Input, Button, Tag, Space, Row, Col, Statistic, message, Spin, Modal, Descriptions } from 'antd'
import { SearchOutlined, DownloadOutlined, EyeOutlined, ArrowUpOutlined, ArrowDownOutlined, ReloadOutlined } from '@ant-design/icons'
import { handleApiRequest } from '../utils/apiClient'
import { mockHotTopics } from '../store/features/hotTopicSlice'

const { Title, Text } = Typography
const { Search } = Input

const PLATFORM_MAP: Record<string, string> = {
  weibo: '微博', wechat: '微信', zhihu: '知乎',
  sina: '新浪', eol: '中国教育在线', jyb: '教育部',
  youth: '中国青年网', sohu: '搜狐', '163': '网易',
}

const SENTIMENT_MAP: Record<string, { color: string; text: string }> = {
  positive: { color: 'success', text: '正面' },
  negative: { color: 'error', text: '负面' },
  neutral: { color: 'default', text: '中性' },
  rising: { color: 'volcano', text: '上升' },
  falling: { color: 'green', text: '下降' },
  stable: { color: 'gold', text: '平稳' },
}

const HotTopicListPage: React.FC = () => {
  const [hotTopics, setHotTopics] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [pagination, setPagination] = useState({ page: 1, pageSize: 10, total: 0 })

  const loadHotTopics = async (page = 1, pageSize = 10) => {
    setLoading(true)
    try {
      const data = await handleApiRequest<{
        items: any[];
        total: number;
        page: number;
        page_size: number;
      }>({
        method: 'GET',
        url: '/api/hot-topic/list',
        params: { page, pageSize },
      })
      if (data.items && data.items.length > 0) {
        setHotTopics(data.items || [])
        setPagination({ page: data.page || page, pageSize: data.page_size || pageSize, total: data.total || 0 })
      } else {
        // API返回空数据时使用mock数据（映射为API返回格式）
        const mapped = mockHotTopics.map(t => ({
          topic: t.title,
          count: t.hot_value,
          sentiment: t.trend_status,
          platforms: t.platforms,
          time_range: `${new Date(t.start_time).toLocaleDateString()} - ${new Date(t.end_time).toLocaleDateString()}`,
          related_opinions: t.related_opinions_count,
        }))
        setHotTopics(mapped)
        setPagination({ page: 1, pageSize, total: mapped.length })
      }
    } catch (error) {
      console.error('加载热点话题失败:', error)
      // API异常时使用mock数据
      const mapped = mockHotTopics.map(t => ({
        topic: t.title,
        count: t.hot_value,
        sentiment: t.trend_status,
        platforms: t.platforms,
        time_range: `${new Date(t.start_time).toLocaleDateString()} - ${new Date(t.end_time).toLocaleDateString()}`,
        related_opinions: t.related_opinions_count,
      }))
      setHotTopics(mapped)
      setPagination({ page: 1, pageSize, total: mapped.length })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHotTopics()
  }, [])

  const stats = {
    totalTopics: pagination.total,
    totalHeat: hotTopics.reduce((sum, t: any) => sum + (t.count || 0), 0),
  }

  const filteredTopics = searchKeyword
    ? hotTopics.filter((t: any) => t.topic?.includes(searchKeyword))
    : hotTopics

  const handleSearch = (value: string) => {
    setSearchKeyword(value)
  }

  const [detailVisible, setDetailVisible] = useState(false)
  const [detailTopic, setDetailTopic] = useState<any>(null)

  const handleExport = () => {
    const csv = [['话题,提及次数,趋势,情感时间范围'].join(',')]
    const rows = filteredTopics.map((t: any) => `"${t.topic}","${t.count}","${t.sentiment}","${t.time_range || ''}"`)
    csv.push(...rows)
    const blob = new Blob(['﻿' + csv.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url
    a.download = 'hot_topics.csv'; a.click(); URL.revokeObjectURL(url)
    message.success('已导出')
  }

  const handleViewDetail = (record: any) => {
    setDetailTopic(record)
    setDetailVisible(true)
  }

  const columns = [
    {
      title: '话题',
      dataIndex: 'topic',
      key: 'topic',
      ellipsis: true,
      width: 300,
      render: (text: string, record: any) => (
        <a onClick={() => handleViewDetail(record)}>{text}</a>
      )
    },
    {
      title: '提及次数',
      dataIndex: 'count',
      key: 'count',
      width: 100,
      sorter: (a: any, b: any) => a.count - b.count,
    },
    {
      title: '趋势',
      dataIndex: 'sentiment',
      key: 'sentiment',
      width: 100,
      render: (val: string) => {
        const info = SENTIMENT_MAP[val] || { color: 'default', text: val || '未知' }
        return <Tag color={info.color}>{info.text}</Tag>
      }
    },
    {
      title: '平台分布',
      dataIndex: 'platforms',
      key: 'platforms',
      width: 250,
      render: (platforms: string[]) => (
        <Space size={4} wrap>
          {(platforms || []).map((p, i) => (
            <Tag key={i} color="blue">{PLATFORM_MAP[p] || p}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: '相关舆情',
      dataIndex: 'related_opinions',
      key: 'related_opinions',
      width: 100,
    },
    {
      title: '时间范围',
      dataIndex: 'time_range',
      key: 'time_range',
      width: 150,
    },
  ]

  return (
    <div>
      <Title level={3}>热点话题管理</Title>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic title="总话题数" value={stats.totalTopics} suffix="个" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic title="总提及次数" value={stats.totalHeat} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <Search
              placeholder="搜索话题"
              onSearch={handleSearch}
              onChange={(e) => setSearchKeyword(e.target.value)}
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
            />
          </div>
          <Button icon={<ReloadOutlined />} onClick={() => loadHotTopics(pagination.page, pagination.pageSize)} loading={loading}>
            刷新数据
          </Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>
            导出数据
          </Button>
        </div>
      </Card>

      <Spin spinning={loading} tip="加载中...">
        <Table
          columns={columns}
          dataSource={filteredTopics}
          rowKey="topic"
          pagination={{
            current: pagination.page,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => loadHotTopics(page, pageSize),
          }}
          scroll={{ x: 'max-content' }}
          locale={{ emptyText: '暂无热点话题数据' }}
        />

        <Modal
          title="热点话题详情"
          open={detailVisible}
          onCancel={() => setDetailVisible(false)}
          footer={<Button onClick={() => setDetailVisible(false)}>关闭</Button>}
          width={640}
        >
          {detailTopic && (
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="话题">{detailTopic.topic}</Descriptions.Item>
              <Descriptions.Item label="提及次数">{detailTopic.count}</Descriptions.Item>
              <Descriptions.Item label="情感趋势">
                <Tag color={detailTopic.sentiment === 'positive' ? 'green' : detailTopic.sentiment === 'negative' ? 'red' : 'blue'}>
                  {detailTopic.sentiment || '未知'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="时间范围">{detailTopic.time_range}</Descriptions.Item>
              <Descriptions.Item label="相关舆情数">{detailTopic.related_opinions}</Descriptions.Item>
              <Descriptions.Item label="平台">
                {(detailTopic.platforms || []).map((p: string) => <Tag key={p}>{p}</Tag>)}
              </Descriptions.Item>
            </Descriptions>
          )}
        </Modal>
      </Spin>
    </div>
  )
}

export default HotTopicListPage
