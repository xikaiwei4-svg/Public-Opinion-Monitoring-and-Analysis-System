import React, { useEffect, useCallback } from 'react'
import { Card, Typography, Select, Button, Spin, Alert, Row, Col } from 'antd'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'
import { useDispatch, useSelector } from 'react-redux'
import { fetchOpinionTrend, fetchSentimentTrend, fetchPlatformDistribution, selectOpinionTrend, selectSentimentTrend, selectPlatformDistribution, selectTrendLoading, selectTrendError, setSelectedPlatform, selectTrendSelectedPlatform } from '../store/features/trendSlice'
import { ArrowUpOutlined, ArrowDownOutlined, FilterOutlined, SyncOutlined } from '@ant-design/icons'

const { Title, Text } = Typography
const { Option } = Select

export interface TrendAnalysisProps {
  timeRange?: string
  onTimeRangeChange?: (value: string) => void
  // 支持直接传递数据的props
  type?: 'line' | 'area' | 'pie'
  data?: any[]
  xField?: string
  yField?: string
  yFields?: string[]
  height?: number
}

const TrendAnalysis: React.FC<TrendAnalysisProps> = ({ 
  timeRange = '7', 
  onTimeRangeChange, 
  type, 
  data, 
  xField, 
  yField, 
  yFields, 
  height 
}) => {
  const dispatch = useDispatch()
  const opinionTrend = useSelector(selectOpinionTrend)
  const sentimentTrend = useSelector(selectSentimentTrend)
  const platformDistribution = useSelector(selectPlatformDistribution)
  const loading = useSelector(selectTrendLoading)
  const error = useSelector(selectTrendError)
  const selectedPlatform = useSelector(selectTrendSelectedPlatform)
  
  // 获取数据
  useEffect(() => {
    // 当有type和data时，使用传递的数据，不自己获取
    // 当有onTimeRangeChange时，由父组件控制数据获取，不自己获取
    if (!type && !data && !onTimeRangeChange) {
      console.log('获取趋势分析数据...');
      dispatch(fetchOpinionTrend({ days: timeRange as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchSentimentTrend({ days: timeRange as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchPlatformDistribution({ days: timeRange as '7' | '15' | '30' }));
    }
  }, [dispatch, type, data, onTimeRangeChange, timeRange, selectedPlatform])

  // 使用实际数据
  const trendData = Array.isArray(opinionTrend) ? opinionTrend : []
  const sentimentData = Array.isArray(sentimentTrend) ? sentimentTrend : []

  // 计算趋势变化
  const calculateTrendChange = (data: any[]) => {
    if (data.length < 2) return { change: 0, percentage: 0 }
    const latest = data[data.length - 1].count
    const previous = data[data.length - 2].count
    const change = latest - previous
    const percentage = previous > 0 ? (change / previous) * 100 : 0
    return { change, percentage }
  }

  const trendChange = calculateTrendChange(trendData)

  // 处理时间范围变化
  const handleTimeRangeChange = useCallback((value: string) => {
    // 通知父组件时间范围变化
    if (onTimeRangeChange) {
      onTimeRangeChange(value)
    } else {
      // 如果没有父组件回调，则直接获取数据
      dispatch(fetchOpinionTrend({ days: value as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchSentimentTrend({ days: value as '7' | '15' | '30', platform: selectedPlatform || undefined }));
      dispatch(fetchPlatformDistribution({ days: value as '7' | '15' | '30' }));
    }
  }, [dispatch, onTimeRangeChange, selectedPlatform])

  // 处理平台选择
  const handlePlatformChange = useCallback((value: string | null) => {
    dispatch(setSelectedPlatform(value));
  }, [dispatch])

  // 刷新数据
  const handleRefresh = useCallback(() => {
    dispatch(fetchOpinionTrend({ days: timeRange, platform: selectedPlatform || undefined }));
    dispatch(fetchSentimentTrend({ days: timeRange, platform: selectedPlatform || undefined }));
    dispatch(fetchPlatformDistribution({ days: timeRange }));
  }, [dispatch, timeRange, selectedPlatform])

  // 如果提供了type和data，渲染指定类型的图表
  if (type && data) {
    return (
      <div style={{ height: height || 300, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          {type === 'line' && yField && (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xField || 'date'} />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Line type="monotone" dataKey={yField} stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          )}
          {type === 'area' && yFields && (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xField || 'date'} />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              {yFields.includes('positive') && <Bar dataKey="positive" name="正面" stackId="a" fill="#52c41a" />}
              {yFields.includes('neutral') && <Bar dataKey="neutral" name="中性" stackId="a" fill="#1890ff" />}
              {yFields.includes('negative') && <Bar dataKey="negative" name="负面" stackId="a" fill="#ff7875" />}
            </BarChart>
          )}
          {type === 'pie' && (
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              />
              <RechartsTooltip />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    )
  }

  // 否则渲染默认的趋势分析图表
  return (
    <div style={{ width: '100%' }}>
      <Card 
        title="趋势分析"
        extra={
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {/* 当有onTimeRangeChange时，不显示时间范围选择器和刷新按钮 */}
            {!onTimeRangeChange && (
              <>
                <Select 
                    value={timeRange} 
                    style={{ width: 100 }} 
                    onChange={handleTimeRangeChange}
                  >
                    <Option value="7">7天</Option>
                    <Option value="14">14天</Option>
                    <Option value="30">30天</Option>
                  </Select>
                <Button 
                  type="primary" 
                  size="small" 
                  icon={<SyncOutlined />}
                  onClick={handleRefresh}
                >
                  刷新
                </Button>
              </>
            )}
            <Select 
              placeholder="选择平台"
              allowClear
              style={{ width: 120 }} 
              value={selectedPlatform} 
              onChange={handlePlatformChange}
            >
              {Array.isArray(platformDistribution) && platformDistribution.map(platform => (
                <Option key={platform.platform} value={platform.platform}>
                  {platform.platform}
                </Option>
              ))}
            </Select>
          </div>
        }
      >
        {error && (
          <Alert 
            message="数据加载失败" 
            description={error} 
            type="error" 
            showIcon 
            style={{ marginBottom: '16px' }}
          />
        )}
        
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <Title level={5}>舆情数量趋势</Title>
            <Text 
              type={trendChange.change >= 0 ? "success" : "danger"}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              {trendChange.percentage.toFixed(1)}%
              {trendChange.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            </Text>
          </div>
          
          <Col span={24}>
              <div style={{ height: '320px', minHeight: '300px' }}>
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <Spin size="large" />
              </div>
            ) : trendData.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#999' }}>
                暂无数据
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={trendData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" orientation="left" stroke="#1890ff" />
                  <YAxis yAxisId="right" orientation="right" stroke="#ff7875" />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="count"
                    name="舆情数量"
                    stroke="#1890ff"
                    activeDot={{ r: 8 }}
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="heat"
                    name="热度指数"
                    stroke="#ff7875"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
</div>
            </Col>
          </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Title level={5}>情感分布趋势</Title>
            <div style={{ height: '320px', minHeight: '300px' }}>
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <Spin size="large" />
              </div>
            ) : sentimentData.length === 0 ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#999' }}>
                暂无数据
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={sentimentData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="positive" name="正面" stackId="a" fill="#52c41a" />
                  <Bar dataKey="neutral" name="中性" stackId="a" fill="#1890ff" />
                  <Bar dataKey="negative" name="负面" stackId="a" fill="#ff7875" />
                </BarChart>
              </ResponsiveContainer>
            )}
</div>
            </Col>
          </Row>
      </Card>
    </div>
  )
}

export default TrendAnalysis
