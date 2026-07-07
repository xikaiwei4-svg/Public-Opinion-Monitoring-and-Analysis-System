import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Spin, Tag, Space, Typography, message, Divider } from 'antd'
import { ArrowLeftOutlined, DownloadOutlined, FilePdfOutlined, FileWordOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'

const { Title, Paragraph } = Typography

interface ReportData {
  id: number
  title: string
  content: string
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

function ReportDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [report, setReport] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/report/${id}`)
      .then(res => res.json())
      .then(d => {
        if (d.code === 200) setReport(d.data)
        else message.error('报告不存在')
      })
      .catch(() => message.error('加载失败'))
      .finally(() => setLoading(false))
  }, [id])

  const handleExportPDF = () => {
    const w = window.open('', '_blank')
    if (!w || !report) return
    const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${report.title}</title>
<style>body{font-family:'PingFang SC','Microsoft YaHei',sans-serif;max-width:800px;margin:0 auto;padding:40px;line-height:1.8;color:#1f2937}
h2{color:#1a56db;border-bottom:2px solid #1a56db;padding-bottom:8px}h3{color:#374151}table{border-collapse:collapse;width:100%}td,th{border:1px solid #e5e7eb;padding:8px 12px}th{background:#f8fafc}
strong{color:#1f2937}blockquote{border-left:3px solid #6366f1;padding-left:16px;color:#6b7280;margin:12px 0}</style></head>
<body>${report.content.replace(/\n/g, '<br>').replace(/^### (.+)$/gm, '<h3>$1</h3>').replace(/^## (.+)$/gm, '<h2>$1</h2>').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}</body></html>`
    w.document.write(html)
    w.document.close()
    setTimeout(() => w.print(), 500)
  }

  const handleExportWord = () => {
    if (!report) return
    const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${report.title}</title></head><body>${report.content.replace(/\n/g, '<br>').replace(/^### (.+)$/gm, '<h3>$1</h3>').replace(/^## (.+)$/gm, '<h2>$1</h2>').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}</body></html>`
    const blob = new Blob([html], { type: 'application/msword' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${report.title}.doc`
    a.click(); URL.revokeObjectURL(url)
    message.success('已导出为 Word 文档')
  }

  const renderMarkdown = (md: string) => {
    return md
      .replace(/^### (.+)$/gm, '<h3 style="margin:20px 0 8px;color:#374151;font-size:15px">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 style="margin:28px 0 12px;color:#1a56db;font-size:18px;border-bottom:2px solid #1a56db;padding-bottom:6px">$1</h2>')
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#1f2937;font-weight:700">$1</strong>')
      .replace(/\n- /g, '\n<li>')
      .replace(/\n\n/g, '</p><p style="margin:8px 0">')
      .replace(/\n/g, '<br>')
      .replace(/---/g, '<hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">')
  }

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 120 }}><Spin size="large" tip="加载报告..." /></div>
  if (!report) return <div style={{ textAlign: 'center', paddingTop: 80, color: '#94a3b8' }}>报告不存在</div>

  return (
    <div style={{ maxWidth: 900 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/report/list')}>返回列表</Button>
        <Button icon={<FilePdfOutlined />} onClick={handleExportPDF}>导出 PDF</Button>
        <Button icon={<FileWordOutlined />} onClick={handleExportWord}>导出 Word</Button>
      </Space>

      <Card className="content-card">
        <div style={{ marginBottom: 8 }}>
          <Space>
            <Tag color={typeMap[report.report_type]?.color}>{typeMap[report.report_type]?.label}</Tag>
            {report.period_start && (
              <span style={{ color: '#94a3b8', fontSize: 13 }}>
                {report.period_start.slice(0, 10)} ~ {report.period_end.slice(0, 10)}
              </span>
            )}
          </Space>
        </div>
        <Title level={3} style={{ margin: '0 0 4px' }}>{report.title}</Title>
        <Paragraph style={{ color: '#94a3b8', fontSize: 12, marginBottom: 20 }}>
          生成时间：{dayjs(report.created_at).format('YYYY-MM-DD HH:mm')} | 数据来源：校园舆情监测系统 | AI 自动生成
        </Paragraph>

        <Divider />

        <div
          className="report-content"
          style={{ lineHeight: 1.9, fontSize: 14, color: '#374151' }}
          dangerouslySetInnerHTML={{ __html: renderMarkdown(report.content) }}
        />
      </Card>
    </div>
  )
}

export default ReportDetailPage
