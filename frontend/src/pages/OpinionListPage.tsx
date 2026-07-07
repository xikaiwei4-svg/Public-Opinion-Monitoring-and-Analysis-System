import { useState, useEffect } from 'react'
import { Typography, Table, Card, Select, Input, Button, DatePicker, Tag, Space, message, Spin, Modal, Descriptions } from 'antd'
import { SearchOutlined, DownloadOutlined, EyeOutlined, DeleteOutlined, ReloadOutlined, LinkOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import {
  fetchOpinions,
  setFilters,
  setCurrentPage,
  setPageSize,
  selectOpinions,
  selectOpinionTotal,
  selectOpinionLoading,
  selectOpinionError,
  selectOpinionFilters,
  selectOpinionCurrentPage,
  selectOpinionPageSize
} from '../store/features/opinionSlice'

const { Title, Text } = Typography
const { Search } = Input
const { RangePicker } = DatePicker

const PLATFORM_COLORS: Record<string, string> = {
  '微博': '#e0245e', '微信': '#07c160', '知乎': '#0066ff', '抖音': '#111111',
  '小红书': '#ff4d4f', 'B站': '#fb7299', '头条': '#e15517',
  '人民网': '#c41230', '人民网教育': '#c41230',
  '新浪教育': '#ff8c00', '中国教育在线': '#1a56db',
}

const OpinionListPage = () => {
  const dispatch = useDispatch()

  const opinions = useSelector(selectOpinions)
  const total = useSelector(selectOpinionTotal)
  const loading = useSelector(selectOpinionLoading)
  const error = useSelector(selectOpinionError)
  const filters = useSelector(selectOpinionFilters)
  const currentPage = useSelector(selectOpinionCurrentPage)
  const pageSize = useSelector(selectOpinionPageSize)

  const [searchKeyword, setSearchKeyword] = useState(filters.keyword || '')
  const [dateRange, setDateRange] = useState<[string, string] | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)
  const [detailItem, setDetailItem] = useState<any>(null)

  useEffect(() => {
    dispatch(fetchOpinions({
      page: currentPage, pageSize, keyword: filters.keyword,
      source: filters.source, sentiment_type: filters.sentiment_type,
      start_time: filters.start_time, end_time: filters.end_time,
    }) as any)
  }, [dispatch, currentPage, pageSize, filters.keyword, filters.source,
      filters.sentiment_type, filters.start_time, filters.end_time])

  const handleSearch = (value: string) => {
    setSearchKeyword(value)
    dispatch(setFilters({ keyword: value }))
    dispatch(setCurrentPage(1))
  }

  const handleSentimentChange = (value: string) => {
    dispatch(setFilters({ sentiment_type: value === 'all' ? '' : value }))
    dispatch(setCurrentPage(1))
  }

  const handleDateRangeChange = (dates: any) => {
    if (dates) {
      const [s, e] = [dates[0].format('YYYY-MM-DD'), dates[1].format('YYYY-MM-DD')]
      setDateRange([s, e])
      dispatch(setFilters({ start_time: s, end_time: e }))
    } else {
      setDateRange(null)
      dispatch(setFilters({ start_time: '', end_time: '' }))
    }
    dispatch(setCurrentPage(1))
  }

  const handleViewDetail = (record: any) => { setDetailItem(record); setDetailVisible(true) }

  const handleOpenSource = (url: string) => {
    if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
      window.open(url, '_blank', 'noopener')
    }
  }

  const handleDelete = async (record: any) => {
    try {
      const res = await fetch(`/api/opinion/${record.id}`, { method: 'DELETE' })
      if (res.ok) { message.success('已删除'); handleRefresh() }
      else { message.error('删除失败') }
    } catch { message.error('删除失败') }
  }

  const handleRefresh = () => {
    dispatch(fetchOpinions({ page: currentPage, pageSize, keyword: filters.keyword,
      source: filters.source, sentiment_type: filters.sentiment_type,
      start_time: filters.start_time, end_time: filters.end_time }) as any)
    message.success('数据已刷新')
  }

  const handleExport = () => {
    const rows = opinions.map((item: any) =>
      [`"${item.id}"`, `"${(item.content || '').slice(0, 120)}"`, `"${item.source_platform || ''}"`,
       `"${item.sentiment_type || ''}"`, `"${item.publish_time || ''}"`, `"${item.url || ''}"`].join(','))
    const csv = ['ID,内容,平台,情感,发布时间,来源链接'].concat(rows).join('\n')
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `opinions_${new Date().toISOString().slice(0, 10)}.csv`
    a.click(); URL.revokeObjectURL(a.href)
    message.success(`已导出 ${opinions.length} 条`)
  }

  const sentimentTagColor: Record<string, string> = { positive: 'success', negative: 'error', neutral: 'default' }
  const sentimentText: Record<string, string> = { positive: '正面', negative: '负面', neutral: '中性' }

  const columns = [
    {
      title: '舆情内容', dataIndex: 'content', key: 'content', ellipsis: true, width: 360,
      render: (text: string, record: any) => (
        <Space>
          <a onClick={() => handleViewDetail(record)} style={{ fontWeight: 500 }}>{text}</a>
          {record.url && (record.url.startsWith('http://') || record.url.startsWith('https://')) && (
            <a onClick={(e) => { e.stopPropagation(); handleOpenSource(record.url) }}
               title="跳转到原始链接" style={{ fontSize: 12, color: '#8b5cf6' }}>
              <LinkOutlined />
            </a>
          )}
        </Space>
      ),
    },
    {
      title: '来源平台', dataIndex: 'source_platform', key: 'platform', width: 110,
      render: (text: string) => {
        const color = PLATFORM_COLORS[text] || '#6366f1'
        return <Tag color={color} style={{ margin: 0 }}>{text}</Tag>
      },
    },
    {
      title: '作者', dataIndex: 'source', key: 'source', width: 100, ellipsis: true,
    },
    {
      title: '发布时间', dataIndex: 'publish_time', key: 'time', width: 150,
      render: (text: string) => text ? new Date(text).toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
      }) : '-',
    },
    {
      title: '情感', dataIndex: 'sentiment_type', key: 'sentiment', width: 80,
      render: (text: string) => <Tag color={sentimentTagColor[text]}>{sentimentText[text] || text}</Tag>,
    },
    { title: '浏览', dataIndex: 'views', key: 'views', width: 70 },
    { title: '点赞', dataIndex: 'likes', key: 'likes', width: 70 },
    { title: '评论', dataIndex: 'comments', key: 'comments', width: 70 },
    { title: '转发', dataIndex: 'shares', key: 'shares', width: 70 },
    {
      title: '操作', key: 'action', width: 100, fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          {record.url && (record.url.startsWith('http://') || record.url.startsWith('https://')) && (
            <Button type="primary" size="small" ghost icon={<LinkOutlined />}
                    onClick={() => handleOpenSource(record.url)}>源站</Button>
          )}
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(record)} />
          <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record)} />
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Title level={3}>舆情管理</Title>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', marginBottom: 16 }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <Search placeholder="搜索内容或关键词" value={searchKeyword}
                    onSearch={handleSearch} onChange={(e) => setSearchKeyword(e.target.value)}
                    allowClear enterButton={<SearchOutlined />} size="middle" />
          </div>
          <Select placeholder="情感筛选" value={filters.sentiment_type || 'all'}
                  onChange={handleSentimentChange} style={{ width: 120 }} size="middle">
            <Select.Option value="all">全部</Select.Option>
            <Select.Option value="positive">正面</Select.Option>
            <Select.Option value="negative">负面</Select.Option>
            <Select.Option value="neutral">中性</Select.Option>
          </Select>
          <RangePicker placeholder={['开始日期', '结束日期']} onChange={handleDateRangeChange}
                       style={{ width: 300 }} size="middle" />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>刷新</Button>
            <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>导出数据</Button>
          </Space>
        </div>
      </Card>

      {error && <div style={{ marginBottom: 16 }}><Typography.Text type="danger">{error}</Typography.Text></div>}

      <Spin spinning={loading}>
        <Table columns={columns} dataSource={opinions} rowKey="id"
          pagination={{
            current: currentPage, pageSize, total,
            showSizeChanger: true, showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, ps) => { dispatch(setCurrentPage(page)); dispatch(setPageSize(ps)) },
          }} scroll={{ x: 1100 }} />

        <Modal title="舆情详情" open={detailVisible} onCancel={() => setDetailVisible(false)}
               footer={<Button onClick={() => setDetailVisible(false)}>关闭</Button>} width={720}>
          {detailItem && (
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="ID">{detailItem.id}</Descriptions.Item>
              <Descriptions.Item label="情感">
                <Tag color={sentimentTagColor[detailItem.sentiment_type]}>
                  {sentimentText[detailItem.sentiment_type] || detailItem.sentiment_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="平台">{detailItem.source_platform}</Descriptions.Item>
              <Descriptions.Item label="作者">{detailItem.source}</Descriptions.Item>
              <Descriptions.Item label="发布时间">{detailItem.publish_time}</Descriptions.Item>
              <Descriptions.Item label="抓取时间">{detailItem.crawl_time}</Descriptions.Item>
              <Descriptions.Item label="内容" span={2}>{detailItem.content}</Descriptions.Item>
              <Descriptions.Item label="浏览量">{detailItem.views}</Descriptions.Item>
              <Descriptions.Item label="点赞">{detailItem.likes}</Descriptions.Item>
              <Descriptions.Item label="评论">{detailItem.comments}</Descriptions.Item>
              <Descriptions.Item label="转发">{detailItem.shares}</Descriptions.Item>
              <Descriptions.Item label="来源链接" span={2}>
                {detailItem.url && (detailItem.url.startsWith('http://') || detailItem.url.startsWith('https://')) ? (
                  <a href={detailItem.url} target="_blank" rel="noopener noreferrer" style={{ color: '#8b5cf6' }}>
                    <LinkOutlined /> {detailItem.url}
                  </a>
                ) : <span style={{ color: '#94a3b8' }}>无有效链接</span>}
              </Descriptions.Item>
            </Descriptions>
          )}
        </Modal>
      </Spin>
    </div>
  )
}

export default OpinionListPage
