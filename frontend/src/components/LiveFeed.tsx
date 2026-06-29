import { useEffect, useState, useRef } from 'react'
import { Tag, Badge, Space } from 'antd'
import { ThunderboltFilled } from '@ant-design/icons'

interface LiveItem {
  id: string; content: string; source_platform: string
  publish_time: string; sentiment: string; sentiment_score: number; keywords: string[]
}

const SENT_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  positive: { color: '#22c55e', bg: '#f0fdf4', label: '正面' },
  negative: { color: '#ef4444', bg: '#fef2f2', label: '负面' },
  neutral: { color: '#6366f1', bg: '#eef2ff', label: '中性' },
}

function LiveFeed() {
  const [items, setItems] = useState<LiveItem[]>([])
  const [count, setCount] = useState(0)
  const [connected, setConnected] = useState(false)
  const eventRef = useRef<EventSource | null>(null)

  useEffect(() => {
    let retryTimer: ReturnType<typeof setTimeout>
    let retryDelay = 2000

    const connect = () => {
      const es = new EventSource('/api/live/stream')
      eventRef.current = es

      es.onopen = () => { setConnected(true); retryDelay = 2000 }
      es.onerror = () => {
        setConnected(false)
        es.close()
        retryTimer = setTimeout(() => { connect() }, retryDelay)
        retryDelay = Math.min(retryDelay * 2, 30000)
      }
      es.onmessage = (event) => {
        try {
          const data: LiveItem = JSON.parse(event.data)
          setItems(prev => [data, ...prev].slice(0, 20))
          setCount(c => c + 1)
        } catch {}
      }
    }

    connect()
    return () => {
      clearTimeout(retryTimer)
      eventRef.current?.close()
    }
  }, [])

  const fmt = (iso: string) => new Date(iso).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <div>
      {/* Status bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <Space>
          <Badge status={connected ? 'processing' : 'default'} />
          <span style={{ fontSize: 13, fontWeight: 600, color: '#1e293b' }}>
            {connected ? '实时监控中' : '等待连接...'}
          </span>
        </Space>
        {connected && (
          <Tag color="green" style={{ borderRadius: 20, padding: '0 10px', fontSize: 11 }}>
            <ThunderboltFilled style={{ marginRight: 4 }} />
            {count} 条
          </Tag>
        )}
      </div>

      {/* Feed list */}
      <div style={{ maxHeight: 340, overflowY: 'auto', paddingRight: 4 }}>
        {items.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '50px 0', color: '#94a3b8', fontSize: 13 }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📡</div>
            等待实时数据推送...
          </div>
        ) : items.map((item) => {
          const cfg = SENT_CONFIG[item.sentiment] || SENT_CONFIG.neutral
          return (
            <div
              key={item.id}
              className="live-item-enter"
              style={{
                padding: '10px 12px', marginBottom: 8,
                backgroundColor: cfg.bg, borderRadius: 10,
                borderLeft: `3px solid ${cfg.color}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
                <Tag color={cfg.color} style={{ fontSize: 10, lineHeight: '16px', margin: 0, borderRadius: 4 }}>
                  {cfg.label} · {Math.round(item.sentiment_score * 100)}%
                </Tag>
                <span style={{ fontSize: 10, color: '#94a3b8' }}>
                  {item.source_platform} · {fmt(item.publish_time)}
                </span>
              </div>
              <div style={{ fontSize: 13, color: '#334155', lineHeight: 1.5 }}>{item.content}</div>
              {item.keywords?.length > 0 && (
                <div style={{ marginTop: 4 }}>
                  {item.keywords.map(kw => (
                    <Tag key={kw} style={{ fontSize: 10, lineHeight: '14px', borderRadius: 4, marginTop: 2 }}>{kw}</Tag>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default LiveFeed
