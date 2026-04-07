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
  Tooltip,
  Empty,
  Typography,
  Form,
  Checkbox,
  message
} from 'antd'
import { SearchOutlined, DownloadOutlined, DeleteOutlined, EyeOutlined, ReloadOutlined, FilterOutlined, AlertOutlined } from '@ant-design/icons'
import { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

import { fetchHotTopics, setFilters, setCurrentPage, setPageSize, selectHotTopics, selectHotTopicCurrentPage, selectHotTopicPageSize, selectHotTopicTotal, selectHotTopicFilters, selectHotTopicLoading } from '../store/features/hotTopicSlice'
import type { RootState } from '../store'
import type { HotTopic } from '../store/features/hotTopicSlice'

const { Title, Text } = Typography
const { RangePicker } = DatePicker
const { Option } = Select
const { Search } = Input

const HotTopicList: React.FC = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  
  // 使用正确的选择器获取数据
  const hotTopics = useSelector(selectHotTopics)
  const currentPage = useSelector(selectHotTopicCurrentPage)
  const pageSize = useSelector(selectHotTopicPageSize)
  const total = useSelector(selectHotTopicTotal)
  const filters = useSelector(selectHotTopicFilters)
  const loading = useSelector(selectHotTopicLoading)
  
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [selectedRows, setSelectedRows] = useState<HotTopic[]>([])
  const [searchForm] = useState<{ resetFields: () => void }>({
    resetFields: () => {}
  })
  const [filterVisible, setFilterVisible] = useState<boolean>(false)
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState<boolean>(false)
  const [currentSort, setCurrentSort] = useState<{ [key: string]: string }>({})
  
  // 趋势状态选项
  const trendOptions = [
    { label: '全部', value: '' },
    { label: '上升', value: 'rising' },
    { label: '下降', value: 'falling' },
    { label: '平稳', value: 'stable' }
  ]
  
  // 话题分类选项
  const categoryOptions = [
    { label: '全部', value: '' },
    { label: '社会', value: 'society' },
    { label: '政治', value: 'politics' },
    { label: '经济', value: 'economy' },
    { label: '文化', value: 'culture' },
    { label: '科技', value: 'technology' },
    { label: '教育', value: 'education' },
    { label: '医疗', value: 'medical' },
    { label: '其他', value: 'other' }
  ]
  
  // 颜色配置
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658']
  
  // 生成趋势图数据
  const generateTrendChartData = () => {
    // 使用数组副本避免直接操作原始数据
    const hotTopicsCopy = [...hotTopics];
    const data = []
    const now = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      const dateStr = date.toLocaleDateString('zh-CN')
      
      // 筛选当天的数据
      const dailyTopics = hotTopicsCopy.filter(topic => {
        const topicDate = new Date(topic.start_time)
        return topicDate.toLocaleDateString('zh-CN') === dateStr
      })
      
      // 计算当天的统计数据
      const totalHeat = dailyTopics.reduce((sum, item) => sum + item.hot_value, 0)
      const averageHeat = dailyTopics.length > 0 ? Math.round(totalHeat / dailyTopics.length) : 0
      const opinionCount = dailyTopics.reduce((sum, item) => sum + item.related_opinions_count, 0)
      
      data.push({
        date: dateStr,
        count: dailyTopics.length,
        averageHeat,
        opinionCount
      })
    }
    
    return data
  }
  
  // 生成话题分类分布数据
  const generateCategoryDistribution = () => {
    // 使用数组副本避免直接操作原始数据
    const hotTopicsCopy = [...hotTopics];
    const categoryCounts: Record<string, number> = {};
    
    hotTopicsCopy.forEach(topic => {
      if (categoryCounts[topic.topic_category]) {
        categoryCounts[topic.topic_category]++;
      } else {
        categoryCounts[topic.topic_category] = 1;
      }
    });
    
    return Object.entries(categoryCounts).map(([name, value]) => ({
      name,
      value
    }));
  }
  
  // 生成情感分布数据
  const generateSentimentDistribution = () => {
    // 使用数组副本避免直接操作原始数据
    const hotTopicsCopy = [...hotTopics];
    
    // 计算所有话题的平均情感分布
    let totalPositive = 0;
    let totalNegative = 0;
    let totalNeutral = 0;
    
    hotTopicsCopy.forEach(topic => {
      totalPositive += topic.sentiment_distribution.positive;
      totalNegative += topic.sentiment_distribution.negative;
      totalNeutral += topic.sentiment_distribution.neutral;
    });
    
    const totalTopics = hotTopicsCopy.length;
    
    return [
      {
        name: '正面',
        value: Math.round(totalPositive / totalTopics),
        percentage: Math.round(totalPositive / totalTopics)
      },
      {
        name: '负面',
        value: Math.round(totalNegative / totalTopics),
        percentage: Math.round(totalNegative / totalTopics)
      },
      {
        name: '中性',
        value: Math.round(totalNeutral / totalTopics),
        percentage: Math.round(totalNeutral / totalTopics)
      }
    ]
  }
  
  // 加载热点话题数据
  const loadHotTopics = () => {
    dispatch(fetchHotTopics({
      page: currentPage,
      pageSize: pageSize,
      ...filters
    }))
  }
  
  // 初始加载和过滤器变更时重新加载数据
  useEffect(() => {
    loadHotTopics()
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
    loadHotTopics()
  }
  
  // 重置筛选条件
  const handleReset = () => {
    searchForm.resetFields()
    dispatch(setFilters({
      keyword: '',
      category: '',
      trend_status: '',
      start_time: '',
      end_time: '',
      min_hot_value: 0
    }))
    dispatch(setCurrentPage(1))
  }
  
  // 表格行选择变化
  const onSelectChange = (newSelectedRowKeys: React.Key[], newSelectedRows: HotTopic[]) => {
    // 创建深拷贝以避免修改不可变的数据
    const rowsCopy = newSelectedRows.map(row => JSON.parse(JSON.stringify(row)));
    setSelectedRows(rowsCopy);
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
  
  // 查看热点话题详情
  const handleViewDetail = (id: string) => {
    navigate(`/hot-topic/detail/${id}`)
  }
  
  // 删除选中热点话题
  const handleDeleteSelected = () => {
    // 在实际项目中，这里应该调用API删除选中的热点话题数据
    message.success(`已删除 ${selectedRows.length} 条热点话题数据`)
    setSelectedRows([])
    setDeleteConfirmVisible(false)
    loadHotTopics() // 重新加载数据
  }
  
  // 删除单条热点话题
  const handleDelete = (id: string) => {
    // 在实际项目中，这里应该调用API删除指定的热点话题数据
    message.success('已删除该热点话题数据')
    loadHotTopics() // 重新加载数据
  }
  
  // 导出数据
  const handleExport = () => {
    // 在实际项目中，这里应该调用API导出数据
    message.success('数据导出成功')
  }
  
  // 获取趋势状态对应的标签样式
  const getTrendTag = (trendStatus: string) => {
    switch (trendStatus) {
      case 'rising':
        return <Tag color="red">上升</Tag>
      case 'falling':
        return <Tag color="green">下降</Tag>
      case 'stable':
        return <Tag color="blue">平稳</Tag>
      default:
        return <Tag>未知</Tag>
    }
  }
  
  // 获取话题分类对应的标签样式
  const getCategoryTag = (category: string) => {
    switch (category) {
      case 'society':
        return <Tag color="blue">社会</Tag>
      case 'politics':
        return <Tag color="red">政治</Tag>
      case 'economy':
        return <Tag color="orange">经济</Tag>
      case 'culture':
        return <Tag color="purple">文化</Tag>
      case 'technology':
        return <Tag color="green">科技</Tag>
      case 'education':
        return <Tag color="cyan">教育</Tag>
      case 'medical':
        return <Tag color="magenta">医疗</Tag>
      case 'other':
        return <Tag color="default">其他</Tag>
      default:
        return <Tag>{category}</Tag>
    }
  }
  
  // 表格列配置
  const columns: ColumnsType<HotTopic> = [
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
      title: '话题标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string) => <Tooltip title={text}>{text}</Tooltip>
    },
    {
      title: '热度值',
      dataIndex: 'hot_value',
      key: 'hot_value',
      width: 80,
      sorter: (a: HotTopic, b: HotTopic) => a.hot_value - b.hot_value
    },
    {
      title: '相关舆情',
      dataIndex: 'related_opinions_count',
      key: 'related_opinions_count',
      width: 80,
      sorter: (a: HotTopic, b: HotTopic) => a.related_opinions_count - b.related_opinions_count
    },
    {
      title: '趋势状态',
      dataIndex: 'trend_status',
      key: 'trend_status',
      width: 80,
      render: (trendStatus: string) => getTrendTag(trendStatus),
      filters: trendOptions.map(option => ({ text: option.label, value: option.value })),
      onFilter: (value: string, record: HotTopic) => record.trend_status === value
    },
    {
      title: '话题分类',
      dataIndex: 'topic_category',
      key: 'topic_category',
      width: 80,
      render: (category: string) => getCategoryTag(category),
      filters: categoryOptions.map(option => ({ text: option.label, value: option.value })),
      onFilter: (value: string, record: HotTopic) => record.topic_category === value
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 160,
      sorter: (a: HotTopic, b: HotTopic) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 120,
      render: (_, record: HotTopic) => (
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
        
        <Form.Item name="category" label="话题分类">
          <Select placeholder="请选择话题分类" allowClear>
            {categoryOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
        </Form.Item>
        
        <Form.Item name="trend_status" label="趋势状态">
          <Select placeholder="请选择趋势状态" allowClear>
            {trendOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
        </Form.Item>
        
        <Form.Item name="min_hot_value" label="最小热度值">
          <Input type="number" placeholder="请输入最小热度值" />
        </Form.Item>
        
        <Form.Item name="timeRange" label="创建时间范围">
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
                    title={`确定要删除选中的 ${selectedRows.length} 条热点话题数据吗？`}
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
          <Card title="话题总数" className="text-center">
            <div className="text-3xl font-bold text-blue-600">{total}</div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="最高热度" className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {hotTopics.length > 0 ? Math.max(...hotTopics.map(item => item.hot_value)) : 0}
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="平均热度" className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {hotTopics.length > 0 
                ? Math.round(hotTopics.reduce((sum, item) => sum + item.hot_value, 0) / hotTopics.length)
                : 0
              }
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card title="舆情总数" className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {hotTopics.length > 0 
                ? hotTopics.reduce((sum, item) => sum + item.opinion_count, 0)
                : 0
              }
            </div>
          </Card>
        </Col>
        
        {/* 趋势图 */}
        <Col span={24}>
          <Card title="热点话题趋势（近7天）">
            {hotTopics.length > 0 ? (
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
                  <Bar dataKey="count" name="话题数量" fill="#8884d8" />
                  <Bar dataKey="averageHeat" name="平均热度" fill="#82ca9d" />
                  <Bar dataKey="opinionCount" name="舆情总数" fill="#ffc658" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="暂无数据" className="py-10" />
            )}
          </Card>
        </Col>
        
        {/* 分布图表 */}
        <Col xs={24} md={12}>
          <Card title="话题分类分布">
            {hotTopics.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={generateCategoryDistribution()}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {generateCategoryDistribution().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => `${value} 个`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="暂无数据" className="py-10" />
            )}
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="情感分布">
            {hotTopics.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
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
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#52c41a' : index === 1 ? '#ff4d4f' : '#1890ff'} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => `${value} 个`} />
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
      <Card title="热点话题列表" className="mt-4">
        <Table
          rowSelection={rowSelection}
          columns={columns}
          // 创建不可变数组副本，避免直接修改Redux state
          dataSource={[...hotTopics]}
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
        onOk={() => {}}
        onCancel={() => setFilterVisible(false)}
        width={600}
        footer={[
          <Button key="reset" onClick={handleReset}>重置</Button>,
          <Button key="cancel" onClick={() => setFilterVisible(false)}>取消</Button>,
          <Button key="confirm" type="primary" onClick={() => setFilterVisible(false)}>确定</Button>
        ]}
      >
        {filterModalContent}
      </Modal>
    </div>
  )
}

export default HotTopicList