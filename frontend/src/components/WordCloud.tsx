import { useEffect, useState, useRef } from 'react'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

interface WordCloudProps {
  height?: number
}

interface WordItem {
  name: string
  value: number
}

function WordCloud({ height = 300 }: WordCloudProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!chartRef.current) return

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    // 先显示模拟数据，再异步加载真实数据
    const mockWords: WordItem[] = [
      { name: '食堂涨价', value: 520 },
      { name: '图书馆', value: 450 },
      { name: '期末考', value: 430 },
      { name: '校园网', value: 380 },
      { name: '奖学金', value: 350 },
      { name: '运动会', value: 320 },
    ]

    const renderChart = (words: WordItem[]) => {
      const option = {
        tooltip: {
          show: true,
          formatter: (params: any) => `${params.name}: ${params.value} 次`,
        },
        series: [
          {
            type: 'wordCloud',
            shape: 'circle',
            left: 'center',
            top: 'center',
            width: '90%',
            height: '90%',
            sizeRange: [10, 48],
            rotationRange: [-45, 45],
            rotationStep: 20,
            gridSize: 6,
            drawOutOfBound: false,
            layoutAnimation: true,
            textStyle: {
              fontFamily: 'sans-serif',
              fontWeight: 'bold',
              color: () => {
                const colors = [
                  '#1890ff', '#52c41a', '#faad14', '#f5222d',
                  '#722ed1', '#13c2c2', '#eb2f96', '#2f54eb',
                  '#fa541c', '#a0d911',
                ]
                return colors[Math.floor(Math.random() * colors.length)]
              },
            },
            emphasis: {
              textStyle: {
                fontSize: 60,
              },
            },
            data: words,
          },
        ],
      }
      chartInstance.current?.setOption(option, true)
    }

    renderChart(mockWords)
    setLoading(false)

    // 异步加载真实词云数据
    fetch('/api/keywords/cloud')
      .then((res) => res.json())
      .then((data) => {
        if (data.words && data.words.length > 0) {
          renderChart(data.words)
        }
      })
      .catch((err) => { console.warn('词云数据加载失败:', err) })

    const handleResize = () => chartInstance.current?.resize()
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <div style={{ position: 'relative', minHeight: height }}>
      {loading && (
        <div style={{ textAlign: 'center', paddingTop: height / 2 - 20, color: '#999' }}>
          加载中...
        </div>
      )}
      <div ref={chartRef} style={{ width: '100%', height }} />
    </div>
  )
}

export default WordCloud
