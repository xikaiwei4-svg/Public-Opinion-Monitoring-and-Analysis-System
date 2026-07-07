import { PlusOutlined, EyeOutlined, DeleteOutlined, FileTextOutlined, BranchesOutlined, AlertOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { Card, Table, Button, Tag, Space, message, Popconfirm, Select, Typography, Input } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
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
  trace: { label: '事件脉络', color: 'magenta' },
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

  const [traceKeyword, setTraceKeyword] = useState('')
  const [tracing, setTracing] = useState(false)
  const [monitoring, setMonitoring] = useState(false)

  const handleMonitor = () => {
    setMonitoring(true)
    message.loading({ content: 'AI正在执行全维度巡检...', key: 'monitor', duration: 0 })
    fetch('/api/report/monitor', { method: 'POST' })
      .then(res => res.json())
      .then(d => {
        message.destroy('monitor')
        if (d.code === 200) { message.success('巡检完成，如有异常已推送微信'); fetchList() }
        else { message.error(d.detail || '巡检失败') }
      })
      .catch(() => { message.destroy('monitor'); message.error('巡检失败') })
      .finally(() => setMonitoring(false))
  }

  const handleTrace = () => {
    if (!traceKeyword.trim()) { message.warning('请输入追踪关键词'); return }
    setTracing(true)
    message.loading({ content: 'AI正在追溯事件脉络，请稍候...', key: 'trace', duration: 0 })
    fetch(`/api/report/trace?keyword=${encodeURIComponent(traceKeyword)}`, { method: 'POST' })
      .then(res => res.json())
      .then(d => {
        message.destroy('trace')
        if (d.code === 200) { message.success('脉络分析完成！'); navigate(`/report/${d.data.id}`) }
        else { message.error(d.detail || '分析失败') }
      })
      .catch(() => { message.destroy('trace'); message.error('分析失败') })
      .finally(() => setTracing(false))
  }

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
          <Button icon={<AlertOutlined />} loading={monitoring} onClick={handleMonitor} style={{ borderColor: '#fa8c16', color: '#fa8c16' }}>一键巡检</Button>
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

      {/* 事件脉络追踪 */}
      <Card className="content-card" style={{ marginTop: 20 }}
        title={<Space><BranchesOutlined style={{ color: '#722ed1' }} /><span style={{ fontWeight: 600 }}>事件脉络追踪</span></Space>}>
        <div style={{ color: '#94a3b8', fontSize: 13, marginBottom: 12 }}>输入关键词，AI 自动追溯话题的完整生命周期：潜伏期 → 爆发期 → 高峰期 → 衰退期</div>
        <Space>
          <Input placeholder="输入话题关键词，如：食堂、考研、宿舍..." value={traceKeyword}
            onChange={e => setTraceKeyword(e.target.value)} onPressEnter={handleTrace}
            style={{ width: 300 }} size="middle" />
          <Button type="primary" icon={<BranchesOutlined />} loading={tracing} onClick={handleTrace}
            style={{ background: '#722ed1', borderColor: '#722ed1' }}>
            开始追踪
          </Button>
        </Space>
      </Card>
    </div>
  )
}

export default ReportListPage
