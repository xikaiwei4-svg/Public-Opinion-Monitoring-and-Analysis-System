import React, { useState, useEffect } from 'react'
import { Typography, Table, Card, Select, Input, Button, DatePicker, Tag, Space, message, Spin } from 'antd'
import { SearchOutlined, CalendarOutlined, FilterOutlined, DownloadOutlined, EyeOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
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

const OpinionListPage: React.FC = () => {
  const dispatch = useDispatch()
  
  const opinions = useSelector(selectOpinions)
  const total = useSelector(selectOpinionTotal)
  const loading = useSelector(selectOpinionLoading)
  const error = useSelector(selectOpinionError)
  const filters = useSelector(selectOpinionFilters)
  const currentPage = useSelector(selectOpinionCurrentPage)
  const pageSize = useSelector(selectOpinionPageSize)

  const [searchKeyword, setSearchKeyword] = useState<string>(filters.keyword || '')
  const [dateRange, setDateRange] = useState<[string, string] | null>(null)

  // 加载数据
  useEffect(() => {
    console.log('OpinionListPage: Loading data...', { currentPage, pageSize, filters })
    dispatch(fetchOpinions({
      page: currentPage,
      pageSize: pageSize,
      keyword: filters.keyword,
      source: filters.source,
      sentiment_type: filters.sentiment_type,
      start_time: filters.start_time,
      end_time: filters.end_time,
      is_sensitive: filters.is_sensitive,
      category: filters.category
    }) as any)
  }, [dispatch, currentPage, pageSize])

  // 调试信息
  useEffect(() => {
    console.log('OpinionListPage: Data updated', { opinions, total, loading, error })
  }, [opinions, total, loading, error])

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value)
    dispatch(setFilters({ keyword: value }))
    dispatch(setCurrentPage(1))
  }

  // 处理情感筛选
  const handleSentimentChange = (value: string) => {
    dispatch(setFilters({ sentiment_type: value === 'all' ? '' : value }))
    dispatch(setCurrentPage(1))
  }

  // 处理日期范围变化
  const handleDateRangeChange = (dates: any) => {
    if (dates) {
      const startDate = dates[0].format('YYYY-MM-DD')
      const endDate = dates[1].format('YYYY-MM-DD')
      setDateRange([startDate, endDate])
      dispatch(setFilters({ start_time: startDate, end_time: endDate }))
      dispatch(setCurrentPage(1))
    } else {
      setDateRange(null)
      dispatch(setFilters({ start_time: '', end_time: '' }))
      dispatch(setCurrentPage(1))
    }
  }

  // 处理导出
  const handleExport = () => {
    message.success('舆情数据已导出')
  }

  // 处理查看详情
  const handleViewDetail = (record: any) => {
    message.info(`查看舆情ID: ${record.id} 的详情`)
  }

  // 处理删除
  const handleDelete = (record: any) => {
    message.success(`已删除舆情ID: ${record.id}`)
    dispatch(fetchOpinions({
      page: currentPage,
      pageSize: pageSize,
      keyword: filters.keyword,
      source: filters.source,
      sentiment_type: filters.sentiment_type,
      start_time: filters.start_time,
      end_time: filters.end_time,
      is_sensitive: filters.is_sensitive,
      category: filters.category
    }) as any)
  }

  // 处理刷新
  const handleRefresh = () => {
    dispatch(fetchOpinions({
      page: currentPage,
      pageSize: pageSize,
      keyword: filters.keyword,
      source: filters.source,
      sentiment_type: filters.sentiment_type,
      start_time: filters.start_time,
      end_time: filters.end_time,
      is_sensitive: filters.is_sensitive,
      category: filters.category
    }) as any)
    message.success('数据已刷新')
  }

  // 情感标签颜色映射
  const sentimentTagColor: Record<string, string> = {
    positive: 'success',
    negative: 'error',
    neutral: 'default'
  }

  // 情感标签文本映射
  const sentimentText: Record<string, string> = {
    positive: '正面',
    negative: '负面',
    neutral: '中性'
  }

  // 表格列配置
  const columns = [
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      width: 400,
      render: (text: string, record: any) => (
        <a onClick={() => handleViewDetail(record)}>{text}</a>
      )
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 120
    },
    {
      title: '平台',
      dataIndex: 'source_platform',
      key: 'source_platform',
      width: 100
    },
    {
      title: '发布时间',
      dataIndex: 'publish_time',
      key: 'publish_time',
      width: 180,
      render: (text: string) => {
        const date = new Date(text)
        return date.toLocaleString('zh-CN', { 
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      }
    },
    {
      title: '情感倾向',
      dataIndex: 'sentiment_type',
      key: 'sentiment_type',
      width: 100,
      render: (text: string) => (
        <Tag color={sentimentTagColor[text]}>{sentimentText[text]}</Tag>
      )
    },
    {
      title: '热度',
      dataIndex: 'heat_score',
      key: 'heat_score',
      width: 80
    },
    {
      title: '浏览量',
      dataIndex: 'views',
      key: 'views',
      width: 80
    },
    {
      title: '敏感',
      dataIndex: 'is_sensitive',
      key: 'is_sensitive',
      width: 80,
      render: (isSensitive: boolean) => (
        isSensitive ? <Tag color="warning">是</Tag> : <Tag>否</Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => handleViewDetail(record)} 
          />
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record)} 
          />
        </Space>
      )
    }
  ]

  return (
    <div>
      <Title level={3}>舆情管理</Title>
      
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', marginBottom: 16 }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <Search
              placeholder="搜索内容或关键词"
              value={searchKeyword}
              onSearch={handleSearch}
              onChange={(e) => setSearchKeyword(e.target.value)}
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
            />
          </div>
          
          <Select
            placeholder="情感筛选"
            value={filters.sentiment_type || 'all'}
            onChange={handleSentimentChange}
            style={{ width: 120 }}
            size="middle"
          >
            <Select.Option value="all">全部</Select.Option>
            <Select.Option value="positive">正面</Select.Option>
            <Select.Option value="negative">负面</Select.Option>
            <Select.Option value="neutral">中性</Select.Option>
          </Select>
          
          <RangePicker
            placeholder={['开始日期', '结束日期']}
            onChange={handleDateRangeChange}
            style={{ width: 300 }}
            size="middle"
          />
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
          <Space>
            <Button 
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={loading}
            >
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              导出数据
            </Button>
          </Space>
        </div>
      </Card>
      
      {error && (
        <div style={{ marginBottom: 16 }}>
          <Typography.Text type="danger">{error}</Typography.Text>
        </div>
      )}
      
      <div style={{ marginBottom: 16, padding: 8, background: '#f0f0f0' }}>
        <Text>调试信息: 加载状态={loading ? '加载中' : '完成'}, 
              数据条数={opinions?.length || 0}, 
              总条数={total}, 
              错误={error || '无'}</Text>
      </div>
      
      <Spin spinning={loading}>
        <Table 
          columns={columns} 
          dataSource={opinions} 
          rowKey="id" 
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              dispatch(setCurrentPage(page))
              dispatch(setPageSize(pageSize))
            }
          }}
          scroll={{ x: 'max-content' }}
        />
      </Spin>
    </div>
  )
}

export default OpinionListPage
