import React, { useRef, useEffect, useMemo } from 'react';
import * as echarts from 'echarts';

interface ChartComponentProps {
  type: 'line' | 'pie' | 'bar';
  data: any[];
  height?: number;
  title?: string;
}

const ChartComponent: React.FC<ChartComponentProps> = ({ 
  type, 
  data, 
  height = 300, 
  title 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // 使用useMemo缓存图表配置，减少重复计算
  const chartOption = useMemo(() => {
    if (!data || data.length === 0) return null;

    let option: echarts.EChartsOption;

    if (type === 'line') {
      // 舆情趋势折线图
      option = {
        title: { text: title || '舆情数量趋势' },
        tooltip: { 
          trigger: 'axis',
          formatter: (params: any) => {
            let result = params[0].name + '<br/>';
            params.forEach((item: any) => {
              result += `${item.marker}${item.seriesName}: ${item.value}<br/>`;
            });
            return result;
          }
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.date),
          axisLabel: { 
            rotate: 45,
            interval: Math.ceil(data.length / 7) - 1 // 只显示部分标签，避免重叠
          }
        },
        yAxis: { 
          type: 'value',
          axisLine: { show: true },
          splitLine: { 
            lineStyle: { 
              type: 'dashed',
              opacity: 0.3
            }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        series: [{
          name: '舆情数量',
          type: 'line',
          data: data.map(item => item.count),
          smooth: true,
          lineStyle: { 
            width: 3,
            shadowColor: 'rgba(24, 144, 255, 0.5)',
            shadowBlur: 10,
            shadowOffsetY: 5
          },
          itemStyle: { 
            color: '#1890ff',
            borderColor: '#fff',
            borderWidth: 2
          },
          areaStyle: { 
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(24, 144, 255, 0.3)'
              }, {
                offset: 1, color: 'rgba(24, 144, 255, 0.05)'
              }]
            }
          },
          symbol: 'circle',
          symbolSize: 8,
          emphasis: {
            focus: 'series',
            itemStyle: { 
              borderWidth: 4,
              borderColor: '#fff'
            }
          }
        }]
      };
    } else if (type === 'pie') {
      // 平台分布饼图
      option = {
        title: { text: title || '平台分布' },
        tooltip: { 
          trigger: 'item', 
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: { 
          orient: 'vertical', 
          left: 'left',
          type: 'scroll',
          top: 'center'
        },
        series: [{
          name: '平台分布',
          type: 'pie',
          radius: ['35%', '65%'],
          center: ['65%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: { 
            label: { 
              show: true, 
              fontSize: 14, 
              fontWeight: 'bold' 
            },
            itemStyle: {
              shadowBlur: 8,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: { show: false },
          data: data
            .filter(item => item.platform !== '其他' && item.count > 0)
            .map(item => ({
              name: item.platform,
              value: item.count
            }))
        }]
      };
    } else if (type === 'bar') {
      // 情感分布柱状图
      option = {
        title: { text: title || '情感分布趋势' },
        tooltip: { 
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: { 
          data: ['正面', '中性', '负面'],
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.date),
          axisLabel: { 
            rotate: 45,
            interval: Math.ceil(data.length / 7) - 1 // 只显示部分标签，避免重叠
          }
        },
        yAxis: { 
          type: 'value',
          axisLine: { show: true },
          splitLine: { 
            lineStyle: { 
              type: 'dashed',
              opacity: 0.3
            }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '20%',
          containLabel: true
        },
        series: [
          { 
            name: '正面', 
            type: 'bar', 
            data: data.map(item => item.positive), 
            itemStyle: { color: '#52c41a' },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(82, 196, 26, 0.5)'
              }
            }
          },
          { 
            name: '中性', 
            type: 'bar', 
            data: data.map(item => item.neutral), 
            itemStyle: { color: '#1890ff' },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(24, 144, 255, 0.5)'
              }
            }
          },
          { 
            name: '负面', 
            type: 'bar', 
            data: data.map(item => item.negative), 
            itemStyle: { color: '#f5222d' },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(245, 34, 45, 0.5)'
              }
            }
          }
        ]
      };
    }

    return option;
  }, [type, data, title]);

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0 || !chartOption) return;

    // 初始化图表实例（只初始化一次）
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, undefined, {
        renderer: 'canvas', // 使用canvas渲染，性能更好
        useDirtyRect: true, // 启用脏矩形渲染，提高性能
        resizePolling: 100 // 调整大小的轮询间隔
      });
    }

    const chart = chartInstance.current;
    
    // 节流处理，避免频繁渲染
    let resizeTimer: NodeJS.Timeout | null = null;
    
    // 响应式调整
    const handleResize = () => {
      if (resizeTimer) {
        clearTimeout(resizeTimer);
      }
      resizeTimer = setTimeout(() => {
        chart.resize();
      }, 100);
    };

    // 设置图表配置
    chart.setOption(chartOption, true); // 第二个参数为true，强制更新所有配置

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (resizeTimer) {
        clearTimeout(resizeTimer);
      }
    };
  }, [chartOption, data.length]); // 只有当chartOption或数据长度变化时才重新渲染

  return <div ref={chartRef} style={{ height, width: '100%' }} />;
};

export default ChartComponent;