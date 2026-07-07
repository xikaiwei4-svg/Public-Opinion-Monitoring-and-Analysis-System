import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Table, Button, Tag, Space, message, Popconfirm, Select, Typography } from 'antd'
import { PlusOutlined, EyeOutlined, DeleteOutlined, FileTextOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Title } = Typography

interface ReportItem {
  id: number
  title: string
  report_type: string
  period_start: string
  period_end: string
  created_at: string
}

const typeMap: Record<string, { label: string; color: string }> = {
  weekly: { label: '周报', color: 'blue' },
  monthly: { label: '月报', color: 'purple' },
  daily: { label: '日报', color: 'green' },
  manual: { label: '手动', color: 'default' },
}

function ReportListPage() {
  const navigate = useNavigate()
  const [data, setData] = useState<ReportItem[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [reportType, setReportType] = useState('weekly')

  const fetchList = () => {
    setLoading(true)
    fetch('/api/report/list?pageSize=20')
      .then(res => res.json())
      .then(d => setData(d.items || []))
      .catch(() => message.error('加载报告列表失败'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchList() }, [])

  const handleGenerate = () => {
    setGenerating(true)
    message.loading({ content: 'AI正在收集数据并生成报告，请稍候...', key: 'gen', duration: 0 })
    fetch(`/api/report/generate?report_type=${reportType}`, { method: 'POST' })
      .then(res => res.json())
      .then(d => {
        message.destroy('gen')
        if (d.code === 200) {
          message.success('报告生成成功！')
          fetchList()
          navigate(`/report/${d.data.id}`)
        } else {
          message.error(d.detail || '报告生成失败')
        }
      })
      .catch(() => {
        message.destroy('gen')
        message.error('生成失败，请检查服务状态')
      })
      .finally(() => setGenerating(false))
  }

  const handleDelete = (id: number) => {
    fetch(`/api/report/${id}`, { method: 'DELETE' })
      .then(res => res.json())
      .then(() => { message.success('已删除'); fetchList() })
      .catch(() => message.error('删除失败'))
  }

  const columns: ColumnsType<ReportItem> = [
    { title: '标题', dataIndex: 'title', key: 'title', width: 300,
      render: (text: string, record: ReportItem) => (
        <a onClick={() => navigate(`/report/${record.id}`)} style={{ fontWeight: 500 }}>{text}</a>
      ),
    },
    { title: '类型', dataIndex: 'report_type', key: 'type', width: 80,
      render: (t: string) => <Tag color={typeMap[t]?.color}>{typeMap[t]?.label || t}</Tag>,
    },
    { title: '报告周期', key: 'period', width: 200,
      render: (_: unknown, r: ReportItem) =>
        r.period_start ? `${r.period_start?.slice(0, 10)} ~ ${r.period_end?.slice(0, 10)}` : '-',
    },
    { title: '生成时间', dataIndex: 'created_at', key: 'created', width: 160,
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    { title: '操作', key: 'actions', width: 120,
      render: (_: unknown, r: ReportItem) => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => navigate(`/report/${r.id}`)}>查看</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={4} style={{ margin: 0 }}>智能报告</Title>
          <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 4 }}>AI 自动分析舆情数据，生成专业报告</div>
        </div>
        <Space>
          <Select value={reportType} onChange={setReportType} style={{ width: 100 }}>
            <Select.Option value="weekly">周报</Select.Option>
            <Select.Option value="monthly">月报</Select.Option>
          </Select>
          <Button type="primary" icon={<PlusOutlined />} loading={generating} onClick={handleGenerate}>
            生成报告
          </Button>
        </Space>
      </div>

      <Card className="content-card">
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: <div style={{ padding: 40 }}><FileTextOutlined style={{ fontSize: 48, color: '#d9d9d9' }} /><div style={{ marginTop: 12, color: '#94a3b8' }}>暂无报告，点击上方按钮生成第一份</div></div> }}
          pagination={{ pageSize: 10, showSizeChanger: false }}
        />
      </Card>
    </div>
  )
}

export default ReportListPage
