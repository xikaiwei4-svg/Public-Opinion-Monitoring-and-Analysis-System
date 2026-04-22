import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';
import { fetchApiData } from '../../utils/apiCache';

// 定义趋势数据类型
export interface TrendDataPoint {
  date: string;
  count: number;
  heat: number;
}

export interface SentimentTrendData {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
}

export interface PlatformDistributionData {
  platform: string;
  count: number;
  percentage: number;
  color: string;
}

export interface TrendState {
  opinionTrend: TrendDataPoint[];
  sentimentTrend: SentimentTrendData[];
  platformDistribution: PlatformDistributionData[];
  loading: boolean;
  error: string | null;
  timeRange: '7' | '15' | '30';
  selectedPlatform: string | null;
}

// 定义初始状态
export const initialState: TrendState = {
  opinionTrend: [],
  sentimentTrend: [],
  platformDistribution: [],
  loading: false,
  error: null,
  timeRange: '7',
  selectedPlatform: null
};

// 工具函数：生成日期范围
const generateDateRange = (days: number): string[] => {
  const dates: string[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(date.toISOString().split('T')[0]);
  }
  return dates;
};

// 工具函数：获取日期字符串
const getDateString = (timestamp: string | undefined): string | null => {
  if (!timestamp) return null;
  try {
    return timestamp.split('T')[0];
  } catch (error) {
    console.error('日期解析失败:', error);
    return null;
  }
};

// 异步获取舆情趋势数据
export const fetchOpinionTrend = createAsyncThunk(
  'trend/fetchOpinionTrend',
  async (params: {
    days: '7' | '15' | '30';
    platform?: string;
  }) => {
    try {
      // 计算日期范围
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - parseInt(params.days));
      
      // 格式化为YYYY-MM-DD
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      // 直接调用后端趋势分析API
      const response = await fetch(`/api/trend/analysis?start_date=${startDateStr}&end_date=${endDateStr}${params.platform ? `&source=${params.platform}` : ''}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const apiData = await response.json();
      
      // 转换数据格式以匹配前端期望的结构
      return apiData.data.trend_data.map((item: any) => ({
        date: item.date,
        count: item.total_count,
        heat: Math.round(item.total_count * 1.5) // 热度值计算
      }));
    } catch (error) {
      console.error('获取舆情趋势数据失败:', error);
      return [];
    }
  }
);

// 异步获取情感趋势数据
export const fetchSentimentTrend = createAsyncThunk(
  'trend/fetchSentimentTrend',
  async (params: {
    days: '7' | '15' | '30';
    platform?: string;
  }) => {
    try {
      // 计算日期范围
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - parseInt(params.days));
      
      // 格式化为YYYY-MM-DD
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      // 直接调用后端情感趋势API
      const response = await fetch(`/api/trend/analysis?start_date=${startDateStr}&end_date=${endDateStr}${params.platform ? `&source=${params.platform}` : ''}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const apiData = await response.json();
      
      // 直接返回API数据，格式已经匹配
      return apiData.data.trend_data.map((item: any) => ({
        date: item.date,
        positive: item.positive_count,
        negative: item.negative_count,
        neutral: item.neutral_count
      }));
    } catch (error) {
      console.error('获取情感趋势数据失败:', error);
      return [];
    }
  }
);

// 异步获取平台分布数据
export const fetchPlatformDistribution = createAsyncThunk(
  'trend/fetchPlatformDistribution',
  async (params: {
    days: '7' | '15' | '30';
  }) => {
    try {
      // 计算日期范围
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - parseInt(params.days));
      
      // 格式化为YYYY-MM-DD
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      // 直接调用后端平台分布API
      const response = await fetch(`/api/trend/analysis/platform?start_date=${startDateStr}&end_date=${endDateStr}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const apiData = await response.json();
      
      const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];
      
      // 平台名称映射
      const platformMap: { [key: string]: string } = {
        'weibo': '微博',
        'wechat': '微信',
        'zhihu': '知乎',
        'sina': '新浪',
        'eol': '中国教育在线',
        'jyb': '教育部',
        'youth': '中国青年网',
        'eduzhixin': '教育信息化',
        'sohu': '搜狐',
        '163': '网易',
        'edu_cn': '中国教育网',
        'ict_edu': '中国教育信息化',
        'ceiea': '中国教育装备网',
        'cscse': '中国留学服务中心',
        'ifeng': '凤凰网',
        'cetv': '中国教育电视台',
        'edu_development': '教育发展',
        'jybpaper': '教育报',
        'eol_news': '中国教育在线新闻',
        'eol_gaokao': '中国教育在线高考',
        'eol_kaoyan': '中国教育在线考研',
        'eol_teacher': '中国教育在线教师',
        'chinakaoyan': '中国考研网',
        'gaokao': '高考网',
        'kaoyanbang': '考研帮',
        'bjeea': '北京教育考试院',
        'shmeea': '上海教育考试院',
        'eeagd': '广东教育考试院'
      };
      
      // 转换数据格式以匹配前端期望的结构
      const transformedData = apiData.data.distribution_data.map((item: any, index: number) => ({
        platform: platformMap[item.platform] || '其他',
        count: item.count,
        percentage: item.percentage,
        color: colors[index % colors.length]
      }));
      
      // 过滤掉"其他"平台和数值过小的平台
      return transformedData.filter(item => item.platform !== '其他' && item.count > 0 && item.percentage > 1);
    } catch (error) {
      console.error('获取平台分布数据失败:', error);
      return [];
    }
  }
);

// 创建slice
const trendSlice = createSlice({
  name: 'trend',
  initialState,
  reducers: {
    setTimeRange: (state, action: PayloadAction<'7' | '15' | '30'>) => {
      state.timeRange = action.payload;
    },
    setSelectedPlatform: (state, action: PayloadAction<string | null>) => {
      state.selectedPlatform = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearTrendData: (state) => {
      state.opinionTrend = [];
      state.sentimentTrend = [];
      state.platformDistribution = [];
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 获取舆情趋势数据
      .addCase(fetchOpinionTrend.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOpinionTrend.fulfilled, (state, action) => {
        state.loading = false;
        state.opinionTrend = action.payload;
      })
      .addCase(fetchOpinionTrend.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取舆情趋势数据失败';
      })
      
      // 获取情感趋势数据
      .addCase(fetchSentimentTrend.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSentimentTrend.fulfilled, (state, action) => {
        state.loading = false;
        state.sentimentTrend = action.payload;
      })
      .addCase(fetchSentimentTrend.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取情感趋势数据失败';
      })
      
      // 获取平台分布数据
      .addCase(fetchPlatformDistribution.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPlatformDistribution.fulfilled, (state, action) => {
        state.loading = false;
        state.platformDistribution = action.payload;
      })
      .addCase(fetchPlatformDistribution.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取平台分布数据失败';
      });
  }
});

// 导出actions
export const { setTimeRange, setSelectedPlatform, clearError, clearTrendData } = trendSlice.actions;

// 导出selectors
export const selectOpinionTrend = (state: RootState) => state.trend.opinionTrend;
export const selectSentimentTrend = (state: RootState) => state.trend.sentimentTrend;
export const selectPlatformDistribution = (state: RootState) => state.trend.platformDistribution;
export const selectTrendLoading = (state: RootState) => state.trend.loading;
export const selectTrendError = (state: RootState) => state.trend.error;
export const selectTrendTimeRange = (state: RootState) => state.trend.timeRange;
export const selectTrendSelectedPlatform = (state: RootState) => state.trend.selectedPlatform;

export default trendSlice.reducer;
