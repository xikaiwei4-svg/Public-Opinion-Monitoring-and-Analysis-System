import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';
import { handleApiRequest } from '../../utils/mockData';

// 定义热点话题数据类型
interface HotTopic {
  id: string;
  title: string;
  description: string;
  keywords: string[];
  related_opinions_count: number;
  start_time: string;
  end_time: string;
  peak_time?: string;
  hot_value: number;
  trend_status: 'rising' | 'stable' | 'falling';
  platforms: string[];
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  topic_category: string;
  is_official?: boolean;
  source_link?: string;
  influencers?: {
    id: string;
    name: string;
    platform: string;
    influence_score: number;
  }[];
}

// 定义话题趋势数据类型
export interface TopicTrendItem {
  date: string;
  hot_value: number;
  opinion_count: number;
}

// 定义话题比较数据类型
export interface TopicComparisonItem {
  id: string;
  title: string;
  hot_value: number;
  change_rate: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  platform_distribution: {
    platform: string;
    count: number;
  }[];
  related_opinions_count: number;
}

// 定义热点话题状态类型
interface HotTopicState {
  list: HotTopic[];
  total: number;
  currentPage: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  selectedTopic: HotTopic | null;
  filters: {
    keyword: string;
    category: string;
    trend_status: string;
    start_time: string;
    end_time: string;
  };
  topicTrend: TopicTrendItem[];
  comparisonData: TopicComparisonItem[];
}

// 模拟热点话题数据
const mockHotTopics: HotTopic[] = [
  {
    id: '1',
    title: '校园图书馆扩建计划获批',
    description: '我校图书馆扩建计划近日获得批准，扩建后图书馆面积将增加一倍，新增各类藏书20万册，并将建设现代化的电子阅读区和学术交流空间。项目预计明年年初完工，将极大改善师生的学习和科研条件。',
    keywords: ['图书馆', '扩建', '学习条件', '科研'],
    related_opinions_count: 235,
    start_time: '2023-09-27T09:00:00',
    end_time: '2023-10-04T09:00:00',
    peak_time: '2023-09-27T14:00:00',
    hot_value: 95,
    trend_status: 'rising',
    platforms: ['微博', '微信公众号', '校园论坛', '知乎'],
    sentiment_distribution: {
      positive: 85,
      negative: 5,
      neutral: 10
    },
    topic_category: 'campus_facility',
    is_official: true,
    source_link: 'https://example.com/topic/1',
    influencers: [
      {
        id: 'inf1',
        name: '校长办公室',
        platform: '微博',
        influence_score: 92
      },
      {
        id: 'inf2',
        name: '图书馆馆长',
        platform: '微信公众号',
        influence_score: 88
      }
    ]
  },
  {
    id: '2',
    title: '食堂菜品质量改善计划',
    description: '为提升学生用餐体验，后勤处启动食堂菜品质量改善计划，邀请专业营养师设计菜单，增加菜品多样性，并严格把控食材质量。同时，食堂将延长营业时间，增设夜宵窗口。',
    keywords: ['食堂', '菜品', '质量改善', '学生生活'],
    related_opinions_count: 189,
    start_time: '2023-09-26T16:45:00',
    end_time: '2023-10-03T16:45:00',
    peak_time: '2023-09-27T12:00:00',
    hot_value: 88,
    trend_status: 'stable',
    platforms: ['微博', '微信公众号', '校园论坛', '知乎'],
    sentiment_distribution: {
      positive: 65,
      negative: 20,
      neutral: 15
    },
    topic_category: 'campus_life',
    is_official: true,
    source_link: 'https://example.com/topic/2',
    influencers: [
      {
        id: 'inf3',
        name: '后勤处处长',
        platform: '校园论坛',
        influence_score: 85
      }
    ]
  },
  {
    id: '3',
    title: '校园运动会报名创新高',
    description: '今年的校园运动会报名人数突破2000人，创历史新高。运动会将增设电子竞技、攀岩等新兴项目，同时保留传统田径项目。开幕式将邀请知名校友回母校表演。',
    keywords: ['运动会', '报名', '创新高', '校园活动'],
    related_opinions_count: 165,
    start_time: '2023-09-25T14:20:00',
    end_time: '2023-10-02T14:20:00',
    peak_time: '2023-09-26T10:00:00',
    hot_value: 82,
    trend_status: 'rising',
    platforms: ['微博', '微信公众号', '校园论坛', '抖音'],
    sentiment_distribution: {
      positive: 72,
      negative: 8,
      neutral: 20
    },
    topic_category: 'campus_life',
    is_official: true,
    source_link: 'https://example.com/topic/3',
    influencers: [
      {
        id: 'inf4',
        name: '校团委书记',
        platform: '微信公众号',
        influence_score: 88
      },
      {
        id: 'inf5',
        name: '体育学院院长',
        platform: '校园论坛',
        influence_score: 82
      }
    ]
  },
  {
    id: '4',
    title: '人工智能学院学术讲座系列',
    description: '人工智能学院将举办"大语言模型与未来"学术讲座系列，邀请国内外知名专家学者前来分享最新研究成果。讲座内容涵盖GPT、BERT等前沿技术，欢迎全校师生参加。',
    keywords: ['人工智能', '学术讲座', '大语言模型', '前沿技术'],
    related_opinions_count: 142,
    start_time: '2023-09-24T10:15:00',
    end_time: '2023-10-01T10:15:00',
    peak_time: '2023-09-25T14:00:00',
    hot_value: 78,
    trend_status: 'stable',
    platforms: ['知乎', '微博', '校园论坛', '微信公众号'],
    sentiment_distribution: {
      positive: 68,
      negative: 5,
      neutral: 27
    },
    topic_category: 'academic_activity',
    is_official: true,
    source_link: 'https://example.com/topic/4',
    influencers: [
      {
        id: 'inf6',
        name: '人工智能学院院长',
        platform: '知乎',
        influence_score: 95
      }
    ]
  },
  {
    id: '5',
    title: '校园网升级完成',
    description: '经过两周的紧张施工，我校校园网升级工程已全部完成。升级后，校园内WiFi覆盖率达到100%，网络带宽提升3倍，下载速度最高可达1Gbps。师生可通过统一认证系统登录校园网，享受高速网络服务。',
    keywords: ['校园网', '升级', 'WiFi', '高速网络'],
    related_opinions_count: 210,
    start_time: '2023-09-23T08:30:00',
    end_time: '2023-09-30T08:30:00',
    peak_time: '2023-09-23T20:00:00',
    hot_value: 90,
    trend_status: 'falling',
    platforms: ['微博', '微信公众号', '校园论坛'],
    sentiment_distribution: {
      positive: 78,
      negative: 12,
      neutral: 10
    },
    topic_category: 'campus_facility',
    is_official: true,
    source_link: 'https://example.com/topic/5',
    influencers: [
      {
        id: 'inf7',
        name: '信息中心主任',
        platform: '校园论坛',
        influence_score: 86
      }
    ]
  }
];

// 模拟话题趋势数据
const mockTopicTrend: TopicTrendItem[] = [
  { date: '9月21日', hot_value: 65, opinion_count: 45 },
  { date: '9月22日', hot_value: 72, opinion_count: 68 },
  { date: '9月23日', hot_value: 85, opinion_count: 92 },
  { date: '9月24日', hot_value: 92, opinion_count: 125 },
  { date: '9月25日', hot_value: 98, opinion_count: 156 },
  { date: '9月26日', hot_value: 105, opinion_count: 189 },
  { date: '9月27日', hot_value: 112, opinion_count: 215 }
];

// 模拟话题比较数据
const mockComparisonData: TopicComparisonItem[] = [
  {
    id: '1',
    title: '校园图书馆扩建计划获批',
    hot_value: 95,
    change_rate: 25,
    sentiment_distribution: {
      positive: 85,
      negative: 5,
      neutral: 10
    },
    platform_distribution: [
      { platform: '微博', count: 125 },
      { platform: '微信公众号', count: 85 },
      { platform: '校园论坛', count: 15 },
      { platform: '知乎', count: 10 }
    ],
    related_opinions_count: 235
  },
  {
    id: '2',
    title: '食堂菜品质量改善计划',
    hot_value: 88,
    change_rate: 12,
    sentiment_distribution: {
      positive: 65,
      negative: 20,
      neutral: 15
    },
    platform_distribution: [
      { platform: '微博', count: 95 },
      { platform: '微信公众号', count: 65 },
      { platform: '校园论坛', count: 25 },
      { platform: '知乎', count: 4 }
    ],
    related_opinions_count: 189
  },
  {
    id: '3',
    title: '校园运动会报名创新高',
    hot_value: 82,
    change_rate: 18,
    sentiment_distribution: {
      positive: 72,
      negative: 8,
      neutral: 20
    },
    platform_distribution: [
      { platform: '微博', count: 85 },
      { platform: '微信公众号', count: 55 },
      { platform: '校园论坛', count: 20 },
      { platform: '抖音', count: 5 }
    ],
    related_opinions_count: 165
  }
];

// 初始状态
const initialState: HotTopicState = {
  list: mockHotTopics,
  total: mockHotTopics.length,
  currentPage: 1,
  pageSize: 10,
  loading: false,
  error: null,
  selectedTopic: null,
  filters: {
    keyword: '',
    category: '',
    trend_status: '',
    start_time: '',
    end_time: ''
  },
  topicTrend: mockTopicTrend,
  comparisonData: mockComparisonData
};

// 异步获取热点话题列表
export const fetchHotTopics = createAsyncThunk(
  'hotTopic/fetchHotTopics',
  async (params: {
    page: number;
    pageSize: number;
    keyword?: string;
    category?: string;
    trend_status?: string;
    start_time?: string;
    end_time?: string;
  }) => {
    try {
      // 修复URL路径，使其与mockData.ts中的处理逻辑匹配
      const data = await handleApiRequest<{
        items: HotTopic[];
        total: number;
        page: number;
        page_size: number;
      }>({
        method: 'GET',
        url: '/api/hot-topic/list',
        params
      });
      return data;
    } catch (error) {
      console.error('获取热点话题列表失败:', error);
      // 直接返回模拟数据作为备用方案
      return {
        items: mockHotTopics,
        total: mockHotTopics.length,
        page: params.page,
        page_size: params.pageSize
      };
    }
  }
);

// 异步获取热点话题详情
export const fetchHotTopicDetail = createAsyncThunk(
  'hotTopic/fetchHotTopicDetail',
  async (id: string) => {
    try {
      const data = await handleApiRequest<HotTopic>({
        method: 'GET',
        url: `/api/hot-topic/${id}`
      });
      return data;
    } catch (error) {
      console.error('获取热点话题详情失败:', error);
      // 返回模拟数据
      return mockHotTopics.find(topic => topic.id === id) || mockHotTopics[0];
    }
  }
);

// 异步获取热点话题趋势数据
export const fetchHotTopicTrend = createAsyncThunk(
  'hotTopic/fetchHotTopicTrend',
  async (params: {
    topic_id: string;
    days: number;
  }) => {
    try {
      const data = await handleApiRequest<TopicTrendItem[]>({
        method: 'GET',
        url: '/api/hot-topic/trend',
        params
      });
      return data;
    } catch (error) {
      console.error('获取热点话题趋势数据失败:', error);
      // 返回模拟数据
      return mockTopicTrend;
    }
  }
);

// 异步比较热点话题
export const compareHotTopics = createAsyncThunk(
  'hotTopic/compareHotTopics',
  async (params: {
    topic_ids: string[];
  }) => {
    try {
      const data = await handleApiRequest<TopicComparisonItem[]>({
        method: 'GET',
        url: '/api/hot-topic/compare',
        params: {
          topic_ids: params.topic_ids.join(',')
        }
      });
      return data;
    } catch (error) {
      console.error('比较热点话题失败:', error);
      return mockComparisonData;
    }
  }
);

// 创建slice
const hotTopicSlice = createSlice({
  name: 'hotTopic',
  initialState,
  reducers: {
    setFilters: (state: { filters: any }, action: PayloadAction<Partial<HotTopicState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setCurrentPage: (state: { currentPage: any }, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state: { pageSize: any }, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    clearSelectedTopic: (state: { selectedTopic: null }) => {
      state.selectedTopic = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 获取热点话题列表
      .addCase(fetchHotTopics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHotTopics.fulfilled, (state, action: { payload: { items: any; total: any; page: any; page_size: any } }) => {
        state.loading = false;
        state.list = action.payload.items;
        state.total = action.payload.total;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchHotTopics.rejected, (state, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取热点话题列表失败';
      })
      
      // 获取热点话题详情
      .addCase(fetchHotTopicDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHotTopicDetail.fulfilled, (state, action: { payload: any }) => {
        state.loading = false;
        state.selectedTopic = action.payload;
      })
      .addCase(fetchHotTopicDetail.rejected, (state, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取热点话题详情失败';
      })
      
      // 获取热点话题趋势数据
      .addCase(fetchHotTopicTrend.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHotTopicTrend.fulfilled, (state, action: { payload: any }) => {
        state.loading = false;
        state.topicTrend = action.payload;
      })
      .addCase(fetchHotTopicTrend.rejected, (state, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取热点话题趋势数据失败';
      })
      
      // 比较热点话题
      .addCase(compareHotTopics.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(compareHotTopics.fulfilled, (state: { loading: boolean; comparisonData: any }, action: { payload: any }) => {
        state.loading = false;
        state.comparisonData = action.payload;
      })
      .addCase(compareHotTopics.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '比较热点话题失败';
      });
  }
});

// 导出actions
export const { setFilters, setCurrentPage, setPageSize, clearSelectedTopic } = hotTopicSlice.actions;

// 导出selectors
export const selectHotTopics = (state: RootState) => state.hotTopic.list;
export const selectHotTopicTotal = (state: RootState) => state.hotTopic.total;
export const selectHotTopicLoading = (state: RootState) => state.hotTopic.loading;
export const selectHotTopicError = (state: RootState) => state.hotTopic.error;
export const selectHotTopicCurrentPage = (state: RootState) => state.hotTopic.currentPage;
export const selectHotTopicPageSize = (state: RootState) => state.hotTopic.pageSize;
export const selectHotTopicFilters = (state: RootState) => state.hotTopic.filters;
export const selectSelectedHotTopic = (state: RootState) => state.hotTopic.selectedTopic;
export const selectSelectedTopic = selectSelectedHotTopic; // 为了向后兼容性，添加别名导出
export const selectHotTopicTrend = (state: RootState) => state.hotTopic.topicTrend;
export const selectHotTopicComparisonData = (state: RootState) => state.hotTopic.comparisonData;

// 导出模拟数据供其他组件使用
export { mockHotTopics, mockTopicTrend, mockComparisonData };

export default hotTopicSlice.reducer;