import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Row,
  Col,
  Statistic,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tabs,
  Descriptions,
  Progress,
  Tooltip,
  Badge,
  Spin
} from 'antd'
import {
  DatabaseOutlined,
  ReloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  CloudServerOutlined,
  TableOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  SettingOutlined,
  PlayCircleOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  getDatabaseStats,
  getCollections,
  getCollectionDetail,
  deleteCollection,
  getDatabaseConfig,
  runCrawler,
  getOpinions
} from '../api/databaseApi'

const { Title } = Typography
const { Option } = Select
const { TextArea } = Input

interface Collection {
  key: string
  name: string
  documentCount: number
  size: string
  avgObjSize: string
  storageSize: string
  indexCount: number
  indexSize: string
  status: 'normal' | 'warning' | 'error'
}

interface DbConfig {
  host: string
  port: number
  database: string
  username: string
  password: string
  authSource: string
  status: 'connected' | 'disconnected'
  lastConnected: string
}

interface DbStats {
  db: string
  collections: number
  views: number
  objects: number
  avgObjSize: number
  dataSize: number
  storageSize: number
  indexes: number
  indexSize: number
  totalSize: number
  fsUsedSize: number
  fsTotalSize: number
}

interface Opinion {
  id: number
  title: string
  content: string
  source_platform: string
  source_url: string
  author: string
  author_id?: string
  publish_time: string
  crawl_time: string
  sentiment: string
  sentiment_score: number
  keywords: string
  read_count: number
  like_count: number
  comment_count: number
  share_count: number
  is_hot: boolean
  hot_score: number
}

const DatabaseManagePage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [collections, setCollections] = useState<Collection[]>([])
  const [dbConfig, setDbConfig] = useState<DbConfig | null>(null)
  const [dbStats, setDbStats] = useState<DbStats | null>(null)
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null)
  const [viewModalVisible, setViewModalVisible] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [crawlerLoading, setCrawlerLoading] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [keywords, setKeywords] = useState<string[]>([])
  const [opinions, setOpinions] = useState<Opinion[]>([])
  const [opinionsLoading, setOpinionsLoading] = useState(false)

  useEffect(() => {
    loadDatabaseData()
    loadOpinions()
  }, [])

  const loadDatabaseData = async () => {
    setLoading(true)
    try {
      const [statsData, collectionsData, configData] = await Promise.all([
        getDatabaseStats(),
        getCollections(),
        getDatabaseConfig()
      ])

      setDbStats(statsData)
      setCollections(collectionsData)
      setDbConfig(configData)
    } catch (error) {
      console.error('加载数据失败:', error)
      message.error('加载数据失败，请检查后端服务是否启动')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    message.info('正在刷新数据...')
    loadDatabaseData()
  }

  const handleViewCollection = async (record: Collection) => {
    try {
      const detail = await getCollectionDetail(record.name)
      setSelectedCollection({ ...record, ...detail })
      setViewModalVisible(true)
    } catch (error) {
      message.error('获取集合详情失败')
    }
  }

  const handleDeleteCollection = async (record: Collection) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除集合 "${record.name}" 吗？此操作不可恢复！`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      async onOk() {
        try {
          await deleteCollection(record.name)
          message.success(`集合 "${record.name}" 已删除`)
          setCollections(collections.filter(item => item.key !== record.key))
        } catch (error) {
          message.error('删除集合失败')
        }
      }
    })
  }

  const handleRunCrawler = async () => {
    setCrawlerLoading(true)
    try {
      const result = await runCrawler(selectedPlatform, keywords.length > 0 ? keywords : undefined)
      message.success(result.message)
      if (result.task_ids) {
        message.info(`任务ID: ${JSON.stringify(result.task_ids)}`)
      } else if (result.task_id) {
        message.info(`任务ID: ${result.task_id}`)
      }
      // 爬虫运行成功后，重新加载数据库数据和舆情数据
      await loadDatabaseData()
      await loadOpinions()
    } catch (error) {
      message.error('运行爬虫任务失败')
    } finally {
      setCrawlerLoading(false)
    }
  }

  const loadOpinions = async () => {
    setOpinionsLoading(true)
    try {
      // 首先获取总数
      const firstBatch = await getOpinions(0, 1)
      const total = firstBatch.total || 0
      
      if (total === 0) {
        setOpinions([])
        return
      }
      
      // 分批加载所有数据，每批1000条
      const batchSize = 1000
      const batches = Math.ceil(total / batchSize)
      let allOpinions: Opinion[] = []
      
      for (let i = 0; i < batches; i++) {
        const skip = i * batchSize
        const limit = Math.min(batchSize, total - skip)
        const batch = await getOpinions(skip, limit)
        allOpinions = [...allOpinions, ...(batch.items || [])]
      }
      
      setOpinions(allOpinions)
      message.success(`已加载 ${allOpinions.length} 条舆情数据`)
    } catch (error) {
      console.error('加载舆情数据失败:', error)
      message.error('加载舆情数据失败')
    } finally {
      setOpinionsLoading(false)
    }
  }

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
  }

  const columns: ColumnsType<Collection> = [
    {
      title: '集合名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => (
        <Space>
          <TableOutlined />
          <span style={{ fontWeight: 500 }}>{text}</span>
        </Space>
      )
    },
    {
      title: '文档数',
      dataIndex: 'documentCount',
      key: 'documentCount',
      sorter: (a, b) => a.documentCount - b.documentCount,
      render: (count) => count.toLocaleString()
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      sorter: (a, b) => parseFloat(a.size) - parseFloat(b.size)
    },
    {
      title: '平均文档大小',
      dataIndex: 'avgObjSize',
      key: 'avgObjSize'
    },
    {
      title: '存储大小',
      dataIndex: 'storageSize',
      key: 'storageSize'
    },
    {
      title: '索引数',
      dataIndex: 'indexCount',
      key: 'indexCount',
      render: (count) => <Tag color="blue">{count}</Tag>
    },
    {
      title: '索引大小',
      dataIndex: 'indexSize',
      key: 'indexSize'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const config = {
          normal: { color: 'success', icon: <CheckCircleOutlined />, text: '正常' },
          warning: { color: 'warning', icon: <WarningOutlined />, text: '警告' },
          error: { color: 'error', icon: <CloseCircleOutlined />, text: '错误' }
        }
        const { color, icon, text } = config[status]
        return (
          <Tag icon={icon} color={color}>
            {text}
          </Tag>
        )
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewCollection(record)}
            />
          </Tooltip>
          <Tooltip title="删除集合">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteCollection(record)}
            />
          </Tooltip>
        </Space>
      )
    }
  ]

  const tabItems = [
    {
      key: 'overview',
      label: (
        <span>
          <CloudServerOutlined />
          概览
        </span>
      ),
      children: (
        <Spin spinning={loading}>
          {dbConfig && (
            <Card style={{ marginBottom: 24 }}>
              <Row gutter={[24, 24]} align="middle">
                <Col span={16}>
                  <Descriptions title="数据库连接信息" bordered column={2}>
                    <Descriptions.Item label="主机">{dbConfig.host}</Descriptions.Item>
                    <Descriptions.Item label="端口">{dbConfig.port}</Descriptions.Item>
                    <Descriptions.Item label="数据库">{dbConfig.database}</Descriptions.Item>
                    <Descriptions.Item label="用户名">{dbConfig.username}</Descriptions.Item>
                    <Descriptions.Item label="认证源">{dbConfig.authSource}</Descriptions.Item>
                    <Descriptions.Item label="最后连接">{dbConfig.lastConnected}</Descriptions.Item>
                  </Descriptions>
                </Col>
                <Col span={8} style={{ textAlign: 'center' }}>
                  <Badge
                    status={dbConfig.status === 'connected' ? 'success' : 'error'}
                    text={dbConfig.status === 'connected' ? '已连接' : '未连接'}
                    style={{ fontSize: 16, marginBottom: 16 }}
                  />
                  <div style={{ fontSize: 48, color: dbConfig.status === 'connected' ? '#52c41a' : '#ff4d4f' }}>
                    <DatabaseOutlined />
                  </div>
                </Col>
              </Row>
            </Card>
          )}

          {dbStats && (
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="总集合数"
                    value={dbStats.collections}
                    prefix={<TableOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="总文档数"
                    value={dbStats.objects}
                    prefix={<FileTextOutlined />}
                    formatter={(value) => (value as number).toLocaleString()}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="数据大小"
                    value={formatBytes(dbStats.dataSize)}
                    prefix={<DatabaseOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="存储大小"
                    value={formatBytes(dbStats.storageSize)}
                    prefix={<CloudServerOutlined />}
                  />
                </Card>
              </Col>
            </Row>
          )}

          {dbStats && (
            <Card title="存储使用情况" style={{ marginBottom: 24 }}>
              <Row gutter={[24, 24]}>
                <Col span={12}>
                  <div style={{ marginBottom: 8 }}>
                    <span>数据存储: {formatBytes(dbStats.dataSize)} / {formatBytes(dbStats.storageSize)}</span>
                  </div>
                  <Progress
                    percent={Math.round((dbStats.dataSize / dbStats.storageSize) * 100)}
                    status="active"
                    strokeColor={{ from: '#108ee9', to: '#87d068' }}
                  />
                </Col>
                <Col span={12}>
                  <div style={{ marginBottom: 8 }}>
                    <span>磁盘使用: {formatBytes(dbStats.fsUsedSize)} / {formatBytes(dbStats.fsTotalSize)}</span>
                  </div>
                  <Progress
                    percent={Math.round((dbStats.fsUsedSize / dbStats.fsTotalSize) * 100)}
                    status="active"
                    strokeColor={{ from: '#108ee9', to: '#87d068' }}
                  />
                </Col>
              </Row>
            </Card>
          )}
        </Spin>
      )
    },
    {
      key: 'collections',
      label: (
        <span>
          <TableOutlined />
          集合管理
        </span>
      ),
      children: (
        <Card>
          <Table
            columns={columns}
            dataSource={collections}
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个集合`
            }}
          />
        </Card>
      )
    },
    {
      key: 'crawler',
      label: (
        <span>
          <PlayCircleOutlined />
          爬虫管理
        </span>
      ),
      children: (
        <Card title="运行爬虫任务">
          <Form layout="vertical" style={{ maxWidth: 600 }}>
            <Form.Item label="选择平台">
              <Select
                value={selectedPlatform}
                onChange={setSelectedPlatform}
                style={{ width: '100%' }}
              >
                <Option value="all">全部平台</Option>
                <Option value="weibo">微博</Option>
                <Option value="wechat">微信</Option>
                <Option value="zhihu">知乎</Option>
              </Select>
            </Form.Item>
            <Form.Item label="关键词（可选，多个关键词用逗号分隔）">
              <Input
                placeholder="例如：校园,学生,教育"
                onChange={(e) => {
                  const value = e.target.value
                  setKeywords(value ? value.split(',').map(k => k.trim()).filter(k => k) : [])
                }}
              />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handleRunCrawler}
                  loading={crawlerLoading}
                >
                  运行爬虫
                </Button>
                <Button onClick={handleRefresh} loading={loading}>
                  刷新数据
                </Button>
              </Space>
            </Form.Item>
          </Form>
          <Card type="inner" title="爬虫说明" style={{ marginTop: 16 }}>
            <p>• 微博爬虫：抓取微博上关于指定关键词的舆情数据</p>
            <p>• 微信爬虫：抓取指定公众号的文章数据</p>
            <p>• 知乎爬虫：抓取指定话题的回答数据</p>
            <p>• 全部平台：同时运行所有爬虫任务</p>
          </Card>
        </Card>
      )
    },
    {
      key: 'opinions',
      label: (
        <span>
          <FileTextOutlined />
          舆情数据
        </span>
      ),
      children: (
        <Card>
          <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
            <Col>
              <Title level={4} style={{ margin: 0 }}>
                舆情数据列表 ({opinions.length} 条)
              </Title>
            </Col>
            <Col>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadOpinions}
                loading={opinionsLoading}
              >
                刷新数据
              </Button>
            </Col>
          </Row>
          <Table
            columns={[
              {
                title: 'ID',
                dataIndex: 'id',
                key: 'id',
                width: 80
              },
              {
                title: '标题',
                dataIndex: 'title',
                key: 'title',
                ellipsis: true,
                render: (text) => <Tooltip title={text}>{text}</Tooltip>
              },
              {
                title: '来源平台',
                dataIndex: 'source_platform',
                key: 'source_platform',
                width: 120,
                render: (text) => <Tag color="blue">{text}</Tag>
              },
              {
                title: '作者',
                dataIndex: 'author',
                key: 'author',
                width: 150,
                ellipsis: true
              },
              {
                title: '情感',
                dataIndex: 'sentiment',
                key: 'sentiment',
                width: 100,
                render: (text) => {
                  const colorMap: Record<string, string> = {
                    positive: 'success',
                    negative: 'error',
                    neutral: 'default'
                  }
                  const labelMap: Record<string, string> = {
                    positive: '正面',
                    negative: '负面',
                    neutral: '中性'
                  }
                  return <Tag color={colorMap[text]}>{labelMap[text]}</Tag>
                }
              },
              {
                title: '发布时间',
                dataIndex: 'publish_time',
                key: 'publish_time',
                width: 180,
                render: (text) => text ? new Date(text).toLocaleString('zh-CN') : '-'
              },
              {
                title: '操作',
                key: 'action',
                width: 100,
                render: (_, record) => (
                  <Button
                    type="link"
                    icon={<EyeOutlined />}
                    onClick={() => window.open(record.source_url, '_blank')}
                  >
                    查看
                  </Button>
                )
              }
            ]}
            dataSource={opinions}
            loading={opinionsLoading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条数据`
            }}
          />
        </Card>
      )
    },
    {
      key: 'config',
      label: (
        <span>
          <SettingOutlined />
          配置管理
        </span>
      ),
      children: (
        <Card title="数据库配置">
          <Form layout="vertical" style={{ maxWidth: 600 }}>
            <Form.Item label="主机地址" required>
              <Input placeholder="localhost" defaultValue={dbConfig?.host || 'localhost'} />
            </Form.Item>
            <Form.Item label="端口" required>
              <Input placeholder="27017" defaultValue={dbConfig?.port || 27017} />
            </Form.Item>
            <Form.Item label="数据库名称" required>
              <Input placeholder="campus_opinion" defaultValue={dbConfig?.database || 'campus_opinion'} />
            </Form.Item>
            <Form.Item label="用户名" required>
              <Input placeholder="admin" defaultValue={dbConfig?.username || ''} />
            </Form.Item>
            <Form.Item label="密码" required>
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
            <Form.Item label="认证源">
              <Input placeholder="admin" defaultValue={dbConfig?.authSource || 'admin'} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary">保存配置</Button>
                <Button>测试连接</Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      )
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            <DatabaseOutlined style={{ marginRight: 12 }} />
            数据库管理
          </Title>
        </Col>
        <Col>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            刷新数据
          </Button>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />

      <Modal
        title="集合详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        {selectedCollection && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="集合名称" span={2}>
              {selectedCollection.name}
            </Descriptions.Item>
            <Descriptions.Item label="文档数量">
              {selectedCollection.documentCount.toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="集合大小">
              {selectedCollection.size}
            </Descriptions.Item>
            <Descriptions.Item label="平均文档大小">
              {selectedCollection.avgObjSize}
            </Descriptions.Item>
            <Descriptions.Item label="存储大小">
              {selectedCollection.storageSize}
            </Descriptions.Item>
            <Descriptions.Item label="索引数量">
              {selectedCollection.indexCount}
            </Descriptions.Item>
            <Descriptions.Item label="索引大小">
              {selectedCollection.indexSize}
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={2}>
              <Tag color={selectedCollection.status === 'normal' ? 'success' : 'warning'}>
                {selectedCollection.status === 'normal' ? '正常' : '警告'}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default DatabaseManagePage
