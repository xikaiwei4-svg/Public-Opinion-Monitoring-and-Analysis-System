import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Input,
  Select,
  DatePicker,
  Button,
  Tag,
  Popconfirm,
  Modal,
  Space,
  Tooltip as AntdTooltip,
  Empty,
  Typography,
  Form,
  message
} from 'antd'
import { SearchOutlined, DownloadOutlined, DeleteOutlined, EyeOutlined, ReloadOutlined, FilterOutlined, AlertOutlined } from '@ant-design/icons'
import { ColumnsType } from 'antd/es/table'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'

import { fetchOpinions, setFilters, setCurrentPage, setPageSize, selectOpinions, selectOpinionCurrentPage, selectOpinionPageSize, selectOpinionTotal, selectOpinionFilters, selectOpinionLoading } from '../store/features/opinionSlice'
import type { RootState } from '../store'
import type { OpinionItem } from '../store/features/opinionSlice'

const { RangePicker } = DatePicker
const { Option } = Select
const { Search } = Input

const OpinionList: React.FC = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  
  // 使用正确的选择器获取数据
  const opinions = useSelector(selectOpinions)
  const currentPage = useSelector(selectOpinionCurrentPage)
  const pageSize = useSelector(selectOpinionPageSize)
  const total = useSelector(selectOpinionTotal)
  const filters = useSelector(selectOpinionFilters)
  const loading = useSelector(selectOpinionLoading)
  
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [selectedRows, setSelectedRows] = useState<OpinionItem[]>([])
  const [searchForm] = useState<{ resetFields: () => void }>({
    resetFields: () => {}
  })
  const [filterVisible, setFilterVisible] = useState<boolean>(false)
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState<boolean>(false)
  const [currentSort, setCurrentSort] = useState<{ [key: string]: string }>({})
  
  // 平台选项
  const platformOptions = [
    { label: '全部', value: '' },
    { label: '微博', value: 'weibo' },
    { label: '微信', value: 'wechat' },
    { label: '抖音', value: 'douyin' },
    { label: '知乎', value: 'zhihu' },
    { label: '小红书', value: 'xiaohongshu' }
  ]
  
  // 情感选项
  const sentimentOptions = [
    { label: '全部', value: '' },
    { label: '正面', value: 'positive' },
    { label: '负面', value: 'negative' },
    { label: '中性', value: 'neutral' }
  ]
  
  // 敏感内容选项
  const sensitiveOptions = [
    { label: '全部', value: null },
    { label: '敏感', value: true },
    { label: '非敏感', value: false }
  ]
  
  // 颜色配置
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658']
  
  // 生成过去7天的趋势数据
  const generateTrendChartData = () => {
    // 使用数组副本避免直接操作原始数据
    const opinionsCopy = [...opinions];
    const data = []
    const now = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      const dateStr = date.toLocaleDateString('zh-CN')
      
      // 筛选当天的数据
      const dailyOpinions = opinionsCopy.filter(opinion => {
        const opinionDate = new Date(opinion.publish_time)
        return opinionDate.toLocaleDateString('zh-CN') === dateStr
      })
      
      // 计算当天的统计数据
      const totalHeat = dailyOpinions.reduce((sum, item) => sum + item.heat_score, 0)
      const averageHeat = dailyOpinions.length > 0 ? Math.round(totalHeat / dailyOpinions.length) : 0
      const sensitiveCount = dailyOpinions.filter(item => item.is_sensitive).length
      
      data.push({
        date: dateStr,
        count: dailyOpinions.length,
        averageHeat,
        sensitiveCount
      })
    }
    
    return data
  }
  
  // 生成情感分布数据
  const generateSentimentDistribution = () => {
    // 使用数组副本避免直接操作原始数据
    const opinionsCopy = [...opinions];
    const positiveCount = opinionsCopy.filter(item => item.sentiment_type === 'positive').length
    const negativeCount = opinionsCopy.filter(item => item.sentiment_type === 'negative').length
    const neutralCount = opinionsCopy.filter(item => item.sentiment_type === 'neutral').length
    
    const total = positiveCount + negativeCount + neutralCount
    
    return [
      {
        name: '正面',
        value: positiveCount,
        percentage: total > 0 ? Math.round((positiveCount / total) * 100) : 0
      },
      {
        name: '负面',
        value: negativeCount,
        percentage: total > 0 ? Math.round((negativeCount / total) * 100) : 0
      },
      {
        name: '中性',
        value: neutralCount,
        percentage: total > 0 ? Math.round((neutralCount / total) * 100) : 0
      }
    ]
  }
  
  // 生成平台分布数据
  const generatePlatformDistribution = () => {
    // 使用数组副本避免直接操作原始数据
    const opinionsCopy = [...opinions];
    const platformCounts: Record<string, number> = {}
    
    opinionsCopy.forEach(item => {
      if (platformCounts[item.source_platform]) {
        platformCounts[item.source_platform]++
      } else {
        platformCounts[item.source_platform] = 1
      }
    })
    
    return Object.entries(platformCounts).map(([name, value]) => ({
      name,
      value
    }))
  }
  
  // 生成敏感内容分布数据
  const generateSensitiveDistribution = () => {
    // 使用数组副本避免直接操作原始数据
    const opinionsCopy = [...opinions];
    const sensitiveCount = opinionsCopy.filter(item => item.is_sensitive).length
    const nonSensitiveCount = opinionsCopy.filter(item => !item.is_sensitive).length
    
    return [
      {
        name: '敏感',
        value: sensitiveCount
      },
      {
        name: '非敏感',
        value: nonSensitiveCount
      }
    ]
  }
  
  // 加载舆情数据
  const loadOpinions = () => {
    dispatch(fetchOpinions({
      page: currentPage,
      pageSize: pageSize,
      ...filters
    }))
  }
  
  // 初始加载和过滤器变更时重新加载数据
  useEffect(() => {
    loadOpinions()
  }, [dispatch, currentPage, pageSize, filters])
  
  // 搜索处理
  const handleSearch = (value: string) => {
    dispatch(setFilters({
      ...filters,
      keyword: value
    }))
    dispatch(setCurrentPage(1))
  }
  
  // 刷新数据
  const handleRefresh = () => {
    loadOpinions()
  }
  
  // 高级筛选
  const handleFilter = (values: any) => {
    // 使用深拷贝创建新对象，避免直接修改filters
    const newFilters = { ...filters };
    
    if (values.keyword) {
      newFilters.keyword = values.keyword
    }
    
    if (values.source_platform) {
      newFilters.source = values.source_platform
    }
    
    if (values.sentiment_type) {
      newFilters.sentiment_type = values.sentiment_type
    }
    
    if (values.is_sensitive !== null) {
      newFilters.is_sensitive = values.is_sensitive
    }
    
    if (values.timeRange && values.timeRange[0] && values.timeRange[1]) {
      newFilters.start_time = values.timeRange[0].format('YYYY-MM-DD')
      newFilters.end_time = values.timeRange[1].format('YYYY-MM-DD')
    }
    
    dispatch(setFilters(newFilters))
    
    // 重置到第一页
    dispatch(setCurrentPage(1))
    
    // 关闭筛选弹窗
    setFilterVisible(false)
  }
  
  // 重置筛选条件
  const handleReset = () => {
    searchForm.resetFields()
    dispatch(setFilters({
      keyword: '',
      source: '',
      sentiment_type: '',
      start_time: '',
      end_time: '',
      is_sensitive: null
    }))
    dispatch(setCurrentPage(1))
  }
  
  // 表格行选择变化
  const onSelectChange = (newSelectedRowKeys: React.Key[], newSelectedRows: OpinionItem[]) => {
    // 创建深拷贝以避免修改不可变的数据
    const rowsCopy = newSelectedRows.map(row => JSON.parse(JSON.stringify(row)));
    setSelectedRows(rowsCopy)
  }
  
  // 表格排序变化
  const handleTableChange = (pagination: any, filters: any, sorter: any) => {
    if (pagination.current !== currentPage) {
      dispatch(setCurrentPage(pagination.current))
    }
    if (pagination.pageSize !== pageSize) {
      dispatch(setPageSize(pagination.pageSize))
    }
    
    // 保存排序信息
    if (sorter.field && sorter.order) {
      setCurrentSort({ [sorter.field]: sorter.order })
    }
  }
  
  // 删除选中舆情
  const handleDeleteSelected = () => {
    // 在实际项目中，这里应该调用API删除选中的舆情数据
    message.success(`已删除 ${selectedRows.length} 条舆情数据`)
    setSelectedRows([])
    setDeleteConfirmVisible(false)
    loadOpinions() // 重新加载数据
  }
  
  // 删除单条舆情
  const handleDelete = (id: string) => {
    // 在实际项目中，这里应该调用API删除指定的舆情数据
    message.success('已删除该舆情数据')
    loadOpinions() // 重新加载数据
  }
  
  // 查看舆情详情
  const handleViewDetail = (id: string) => {
    navigate(`/opinion/detail/${id}`)
  }
  
  // 导出数据
  const handleExport = () => {
    // 在实际项目中，这里应该调用API导出数据
    message.success('数据导出成功')
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
  
  // 表格列配置
  const columns: ColumnsType<OpinionItem> = [
    {
      title: '复选框',
      key: 'selection',
      fixed: 'left',
      width: 60,
      render: () => <Checkbox />
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (text: string) => <AntdTooltip title={text}>{text}</AntdTooltip>
    },
    {
      title: '来源平台',
      dataIndex: 'source_platform',
      key: 'source_platform',
      width: 100,
      filters: platformOptions.map(option => ({ text: option.label, value: option.value })),
      onFilter: (value: string, record: OpinionItem) => record.source_platform === value
    },
    {
      title: '发布时间',
      dataIndex: 'publish_time',
      key: 'publish_time',
      width: 160,
      sorter: (a: OpinionItem, b: OpinionItem) => new Date(a.publish_time).getTime() - new Date(b.publish_time).getTime()
    },
    {
      title: '情感倾向',
      dataIndex: 'sentiment_type',
      key: 'sentiment_type',
      width: 100,
      render: (sentimentType: string) => getSentimentTag(sentimentType),
      filters: sentimentOptions.map(option => ({ text: option.label, value: option.value })),
      onFilter: (value: string, record: OpinionItem) => record.sentiment_type === value
    },
    {
      title: '热度',
      dataIndex: 'heat_score',
      key: 'heat_score',
      width: 80,
      sorter: (a: OpinionItem, b: OpinionItem) => a.heat_score - b.heat_score
    },
    {
      title: '敏感内容',
      key: 'sensitive',
      width: 100,
      render: (_, record: OpinionItem) => getSensitiveTag(record.is_sensitive, record.sensitive_level)
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 120,
      render: (_, record: OpinionItem) => (
        <Space size="middle">
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(record.id)}>查看</Button>
          <Popconfirm
            title="确认删除？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ]
  
  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange
  }
  
  // 高级筛选弹窗内容
  const filterModalContent = (
    <div>
      <Form layout="vertical">
        <Form.Item name="keyword" label="关键词">
          <Input placeholder="请输入关键词" />
        </Form.Item>
        
        <Form.Item name="source_platform" label="来源平台">
          <Select placeholder="请选择来源平台" allowClear>
            {platformOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
        </Form.Item>
        
        <Form.Item name="sentiment_type" label="情感倾向">
          <Select placeholder="请选择情感倾向" allowClear>
            {sentimentOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
        </Form.Item>
        
        <Form.Item name="is_sensitive" label="敏感内容">
          <Select placeholder="请选择敏感内容" allowClear>
            {sensitiveOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
        </Form.Item>
        
        <Form.Item name="timeRange" label="发布时间范围">
          <RangePicker />
        </Form.Item>
      </Form>
    </div>
  )
  
  return (
    <div className="p-4">
      <Row gutter={[16, 16]}>
        {/* 顶部搜索栏 */}
        <Col span={24}>
          <Card className="mb-4">
            <Row gutter={[16, 0]}>
              <Col flex="auto">
                <Search
                  placeholder="请输入关键词搜索"
                  allowClear
                  enterButton={<SearchOutlined />}
                  size="large"
                  onSearch={handleSearch}
                />
              </Col>
              <Col>
                <Button icon={<ReloadOutlined />} onClick={handleRefresh}>刷新</Button>
              </Col>
              <Col>
                <Button icon={<DownloadOutlined />} onClick={handleExport}>导出</Button>
              </Col>
              <Col>
                <Button onClick={() => setFilterVisible(true)}>高级筛选</Button>
              </Col>
              {selectedRows.length > 0 && (
                <Col>
                  <Popconfirm
                    title={`确定要删除选中的 ${selectedRows.length} 条舆情数据吗？`}
                    onConfirm={handleDeleteSelected}
                    okText="确定"
                    cancelText="取消"
                    open={deleteConfirmVisible}
                    onOpenChange={setDeleteConfirmVisible}
                  >
                    <Button danger>删除选中</Button>
                  </Popconfirm>
                </Col>
              )}
            </Row>
          </Card>
        </Col>
        
        {/* 数据统计卡片 */}
        <Col xs={24} sm={12} md={6}>
          <Card title="舆情总数" className="text-center">
            <div className="text-3xl font-bold text-blue-600">{total}</div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="敏感内容" className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {opinions.filter(item => item.is_sensitive).length}
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="平均热度" className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {opinions.length > 0 
                ? Math.round(opinions.reduce((sum, item) => sum + item.heat_score, 0) / opinions.length)
                : 0
              }
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="最新数据" className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {opinions.length > 0 
                ? new Date(Math.max(...opinions.map(item => new Date(item.publish_time).getTime()))).toLocaleDateString('zh-CN')
                : '-'}
            </div>
          </Card>
        </Col>
        
        {/* 趋势图 */}
        <Col span={24}>
          <Card title="舆情趋势（近7天）">
            {opinions.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={generateTrendChartData()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="count" name="舆情数量" fill="#8884d8" />
                  <Bar dataKey="averageHeat" name="平均热度" fill="#82ca9d" />
                  <Bar dataKey="sensitiveCount" name="敏感数量" fill="#ffc658" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="暂无数据" className="py-10" />
            )}
          </Card>
        </Col>
        
        {/* 分布图表 */}
        <Col xs={24} md={12}>
          <Card title="情感分布">
            {opinions.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={generateSentimentDistribution()}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {generateSentimentDistribution().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => `${value} 条`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="暂无数据" className="py-10" />
            )}
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="敏感内容分布">
            {opinions.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={generateSensitiveDistribution()}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {generateSensitiveDistribution().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#ff4d4f' : '#52c41a'} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => `${value} 条`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="暂无数据" className="py-10" />
            )}
          </Card>
        </Col>
      </Row>
      
      {/* 表格区域 */}
      <Card title="舆情列表" className="mt-4">
        <Table
          rowSelection={rowSelection}
          columns={columns}
          // 创建不可变数组副本，避免直接修改Redux state
          dataSource={[...opinions]}
          loading={loading}
          rowKey="id"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条数据`,
            pageSizeOptions: ['10', '20', '50', '100']
          }}
          onChange={handleTableChange}
          scroll={{ x: 'max-content' }}
        />
      </Card>
      
      {/* 高级筛选弹窗 */}
      <Modal
        title="高级筛选"
        open={filterVisible}
        onOk={() => handleFilter({})}
        onCancel={() => setFilterVisible(false)}
        width={600}
        footer={[
          <Button key="reset" onClick={handleReset}>重置</Button>,
          <Button key="cancel" onClick={() => setFilterVisible(false)}>取消</Button>,
          <Button key="confirm" type="primary" onClick={() => handleFilter({})}>确定</Button>
        ]}
      >
        {filterModalContent}
      </Modal>
    </div>
  )
}

export default OpinionList