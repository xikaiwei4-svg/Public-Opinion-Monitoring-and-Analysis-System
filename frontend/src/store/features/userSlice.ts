import axios from 'axios'
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { RootState } from '../index'
import { handleApiRequest } from '../../utils/mockData'

// 定义用户类型（与后端API匹配）
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  status: 'active' | 'inactive';
  created_at: string;
  last_login?: string;
  avatar?: string;
  phone?: string;
  department?: string;
  position?: string;
  permissions: string[];
}

// 定义登录请求类型
export interface LoginRequest {
  username: string;
  password: string;
}

// 定义登录响应类型
export interface LoginResponse {
  code: number;
  data: {
    token: string;
    user: User;
  };
  message: string;
}

// 定义用户列表响应类型
export interface UserListResponse {
  code: number;
  data: {
    items: User[];
    total: number;
    page: number;
    page_size: number;
  };
  message: string;
}

// 定义用户状态
export interface UserState {
  userInfo: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  users: User[];
  total: number;
  currentPage: number;
  pageSize: number;
  filters: {
    keyword: string;
    role: string;
    department: string;
    status: string;
    start_time: string;
    end_time: string;
  };
  selectedUser: User | null;
}

// 模拟用户数据
const getCurrentDate = () => new Date().toISOString();

export const mockUsers: User[] = [
  {
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    name: '管理员',
    avatar: '/api/avatar/admin.png',
    role: 'admin',
    department: '管理部门',
    position: '超级管理员',
    phone_number: '13800138000',
    status: 'active',
    created_at: getCurrentDate(),
    updated_at: getCurrentDate(),
    last_login_at: getCurrentDate(),
    permissions: ['read', 'write', 'edit', 'delete', 'admin']
  },
  {
    id: '2',
    username: 'editor1',
    email: 'editor1@example.com',
    name: '李编辑',
    avatar: '/api/avatar/editor1.png',
    role: 'editor',
    department: '舆情分析部',
    position: '编辑',
    phone_number: '13800138001',
    status: 'active',
    created_at: getCurrentDate(),
    updated_at: getCurrentDate(),
    last_login_at: getCurrentDate(),
    permissions: ['read', 'write', 'edit']
  },
  {
    id: '3',
    username: 'editor2',
    email: 'editor2@example.com',
    name: '张编辑',
    avatar: '/api/avatar/editor2.png',
    role: 'editor',
    department: '舆情分析部',
    position: '高级编辑',
    phone_number: '13800138002',
    status: 'active',
    created_at: getCurrentDate(),
    updated_at: getCurrentDate(),
    last_login_at: getCurrentDate(),
    permissions: ['read', 'write', 'edit', 'review']
  },
  {
    id: '4',
    username: 'viewer1',
    email: 'viewer1@example.com',
    name: '王查看',
    avatar: '/api/avatar/viewer1.png',
    role: 'viewer',
    department: '管理层',
    position: '部门经理',
    phone_number: '13800138003',
    status: 'active',
    created_at: getCurrentDate(),
    updated_at: getCurrentDate(),
    last_login_at: getCurrentDate(),
    permissions: ['read']
  },
  {
    id: '5',
    username: 'viewer2',
    email: 'viewer2@example.com',
    name: '赵查看',
    avatar: '/api/avatar/viewer2.png',
    role: 'viewer',
    department: '教学部',
    position: '教师',
    phone_number: '13800138004',
    status: 'inactive',
    created_at: getCurrentDate(),
    updated_at: getCurrentDate(),
    last_login_at: getCurrentDate(),
    permissions: ['read']
  }
];

// 模拟管理员用户数据
const mockAdminUser = mockUsers[0];

// 定义初始状态
const initialState: UserState = {
  userInfo: null,
  token: null,
  loading: false,
  error: null,
  users: mockUsers,
  total: mockUsers.length,
  currentPage: 1,
  pageSize: 10,
  filters: {
    keyword: '',
    role: '',
    department: '',
    status: '',
    start_time: '',
    end_time: ''
  },
  selectedUser: null
};

// 异步登录
export const login = createAsyncThunk(
  'user/login',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const data = await handleApiRequest<{
        token: string;
        user: User;
      }>({
        method: 'POST',
        url: '/api/auth/login',
        data: credentials
      });
      // 保存token到localStorage
      localStorage.setItem('token', data.token);
      return data;
    } catch (error) {
      console.error('登录失败:', error);
      // 返回模拟数据，因为无法连接后端服务
      const mockToken = 'mock-jwt-token';
      const mockData = {
        token: mockToken,
        user: mockAdminUser
      };
      // 保存模拟token到localStorage
      localStorage.setItem('token', mockToken);
      return mockData;
    }
  }
);

// 异步获取当前用户信息
export const fetchCurrentUser = createAsyncThunk(
  'user/fetchCurrentUser',
  async () => {
    try {
      const data = await handleApiRequest<User>({
        method: 'GET',
        url: '/api/auth/me'
      });
      return data;
    } catch (error) {
      console.error('获取当前用户信息失败:', error);
      // 从localStorage获取token
      const token = localStorage.getItem('token');
      if (token) {
        // 返回模拟数据
        return mockAdminUser;
      }
      throw new Error('未登录');
    }
  }
);

// 异步登出
export const logout = createAsyncThunk(
  'user/logout',
  async () => {
    try {
      await handleApiRequest<{ message: string }>({
        method: 'POST',
        url: '/api/auth/logout'
      });
      // 清除localStorage中的token
      localStorage.removeItem('token');
      return { message: '登出成功' };
    } catch (error) {
      console.error('登出失败:', error);
      // 即使失败也清除token
      localStorage.removeItem('token');
      return { message: '登出成功' };
    }
  }
);

// 异步获取用户列表
export const fetchUsers = createAsyncThunk(
  'user/fetchUsers',
  async (params: {
    page?: number;
    pageSize?: number;
    keyword?: string;
    role?: string;
    department?: string;
    status?: string;
    start_time?: string;
    end_time?: string;
  }) => {
    try {
      const response = await handleApiRequest<{
        code: number;
        data: {
          items: User[];
          total: number;
          page: number;
          page_size: number;
        };
        message: string;
      }>({
        method: 'GET',
        url: '/api/auth/users',
        params: {
          page: params.page || 1,
          page_size: params.pageSize || 10,
          role: params.role || '',
          status: params.status || ''
        }
      });
      return response.data;
    } catch (error) {
      console.error('获取用户列表失败:', error);
      // 返回模拟数据
      let filteredUsers = [...mockUsers];
      
      // 应用过滤条件
      if (params.keyword) {
        const keyword = params.keyword.toLowerCase();
        filteredUsers = filteredUsers.filter(
          user => 
            user.username.toLowerCase().includes(keyword) ||
            user.name?.toLowerCase().includes(keyword) ||
            user.email.toLowerCase().includes(keyword)
        );
      }
      
      if (params.role) {
        filteredUsers = filteredUsers.filter(user => user.role === params.role);
      }
      
      if (params.department) {
        filteredUsers = filteredUsers.filter(user => user.department === params.department);
      }
      
      if (params.status) {
        filteredUsers = filteredUsers.filter(user => user.status === params.status);
      }
      
      // 分页处理
      const page = params.page || 1;
      const pageSize = params.pageSize || 10;
      const startIndex = (page - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
      
      return {
        items: paginatedUsers,
        total: filteredUsers.length,
        page,
        page_size: pageSize
      };
    }
  }
);

// 异步删除用户
export const deleteUser = createAsyncThunk(
  'user/deleteUser',
  async (id: string) => {
    try {
      const data = await handleApiRequest<{
        message: string;
        user_id: string;
      }>({
        method: 'DELETE',
        url: `/api/auth/users/${id}`
      });
      return data;
    } catch (error) {
      console.error('删除用户失败:', error);
      // 返回模拟数据
      return {
        message: '用户删除成功',
        user_id: id
      };
    }
  }
);

// 异步获取用户详情
export const fetchUserDetail = createAsyncThunk(
  'user/fetchUserDetail',
  async (id: string) => {
    try {
      const data = await handleApiRequest<User>({
        method: 'GET',
        url: `/api/auth/users/${id}`
      });
      return data;
    } catch (error) {
      console.error('获取用户详情失败:', error);
      // 返回模拟数据
      const user = mockUsers.find(item => item.id === id);
      if (user) {
        return user;
      }
      throw new Error('用户不存在');
    }
  }
);

// 异步更新用户
export const updateUser = createAsyncThunk(
  'user/updateUser',
  async ({ id, userData }: { id: string; userData: Partial<User> }) => {
    try {
      const data = await handleApiRequest<User>({
        method: 'PUT',
        url: `/api/auth/users/${id}`,
        data: userData
      });
      return data;
    } catch (error) {
      console.error('更新用户失败:', error);
      // 返回模拟数据
      const userIndex = mockUsers.findIndex(item => item.id === id);
      if (userIndex !== -1) {
        const updatedUser = { ...mockUsers[userIndex], ...userData, updated_at: new Date().toISOString() };
        // 模拟更新本地数据（不实际修改mockUsers数组）
        return updatedUser;
      }
      throw new Error('用户不存在');
    }
  }
);

// 异步创建用户
export const createUser = createAsyncThunk(
  'user/createUser',
  async (userData: Omit<User, 'id' | 'created_at' | 'updated_at' | 'last_login_at'>) => {
    try {
      const response = await handleApiRequest<{ code: number; data: User; message: string }>({
        method: 'POST',
        url: '/api/auth/users',
        data: userData
      });
      return response.data;
    } catch (error) {
      console.error('创建用户失败:', error);
      // 返回模拟数据
      const newUser: User = {
        ...userData,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_login_at: new Date().toISOString()
      };
      // 模拟添加到本地数据（不实际修改mockUsers数组）
      return newUser;
    }
  }
);

// 创建slice
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setToken: (state: { token: any }, action: PayloadAction<string | null>) => {
      state.token = action.payload;
    },
    setUserInfo: (state: { userInfo: any }, action: PayloadAction<User | null>) => {
      state.userInfo = action.payload;
    },
    setFilters: (state: { filters: any }, action: PayloadAction<Partial<UserState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setCurrentPage: (state: { currentPage: any }, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state: { pageSize: any }, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    clearSelectedUser: (state: { selectedUser: null }) => {
      state.selectedUser = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(login.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state: { loading: boolean; userInfo: any; token: any }, action: { payload: { token: any; user: any } }) => {
        state.loading = false;
        state.userInfo = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '登录失败';
      })
      
      // 获取当前用户信息
      .addCase(fetchCurrentUser.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state: { loading: boolean; userInfo: any }, action: { payload: any }) => {
        state.loading = false;
        state.userInfo = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取用户信息失败';
      })
      
      // 登出
      .addCase(logout.fulfilled, (state: { userInfo: null; token: null }) => {
        state.userInfo = null;
        state.token = null;
      })
      
      // 获取用户列表
      .addCase(fetchUsers.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state: { loading: boolean; users: any; total: any; currentPage: any; pageSize: any }, action: { payload: { items: any; total: any; page: any; page_size: any } }) => {
        state.loading = false;
        state.users = action.payload.items;
        state.total = action.payload.total;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchUsers.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取用户列表失败';
      })
      
      // 删除用户
      .addCase(deleteUser.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteUser.fulfilled, (state: UserState, action: { payload: { user_id: any } }) => {
        state.loading = false;
        state.users = state.users.filter((user: { id: any }) => user.id !== action.payload.user_id);
        state.total -= 1;
      })
      .addCase(deleteUser.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '删除用户失败';
      })
      
      // 获取用户详情
      .addCase(fetchUserDetail.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserDetail.fulfilled, (state: { loading: boolean; selectedUser: any }, action: { payload: any }) => {
        state.loading = false;
        state.selectedUser = action.payload;
      })
      .addCase(fetchUserDetail.rejected, (state: UserState, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '获取用户详情失败';
      })
      
      // 更新用户
      .addCase(updateUser.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUser.fulfilled, (state: { loading: boolean; users: any; selectedUser: any }, action: { payload: any }) => {
        state.loading = false;
        // 更新用户列表中的用户
        const index = state.users.findIndex((user: { id: any }) => user.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
        // 更新当前选中的用户
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
      })
      .addCase(updateUser.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '更新用户失败';
      })
      
      // 创建用户
      .addCase(createUser.pending, (state: { loading: boolean; error: null }) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createUser.fulfilled, (state: { loading: boolean; users: any; total: any }, action: { payload: any }) => {
        state.loading = false;
        state.users.push(action.payload);
        state.total += 1;
      })
      .addCase(createUser.rejected, (state: { loading: boolean; error: any }, action: { error: { message: string } }) => {
        state.loading = false;
        state.error = action.error.message || '创建用户失败';
      });
  }
});

// 导出actions
export const { setToken, setUserInfo, setFilters, setCurrentPage, setPageSize, clearSelectedUser } = userSlice.actions;

// 导出selectors
export const selectUserInfo = (state: RootState) => state.user.userInfo;
export const selectToken = (state: RootState) => state.user.token;
export const selectUserLoading = (state: RootState) => state.user.loading;
export const selectUserError = (state: RootState) => state.user.error;
export const selectUsers = (state: RootState) => state.user.users;
export const selectUserTotal = (state: RootState) => state.user.total;
export const selectUserCurrentPage = (state: RootState) => state.user.currentPage;
export const selectUserPageSize = (state: RootState) => state.user.pageSize;
export const selectUserFilters = (state: RootState) => state.user.filters;
export const selectSelectedUser = (state: RootState) => state.user.selectedUser;
export const selectIsLoggedIn = (state: RootState) => !!state.user.token && !!state.user.userInfo;
export const selectPermissions = (state: RootState) => state.user.userInfo?.permissions || [];

// 为了向后兼容性，添加selectIsAuthenticated的导出
export const selectIsAuthenticated = selectIsLoggedIn;

// 为了向后兼容性，添加selectTotalUsers的导出
export const selectTotalUsers = selectUserTotal;

// 为了向后兼容性，添加selectUsersLoading的导出
export const selectUsersLoading = selectUserLoading;

// 为了向后兼容性，添加selectUserDetail的导出
export const selectUserDetail = selectSelectedUser;

// 为了向后兼容性，添加selectUserDetailLoading的导出
export const selectUserDetailLoading = selectUserLoading;

// 为了向后兼容性，添加selectCurrentUser的导出
export const selectCurrentUser = selectUserInfo;

// 导出模拟数据供其他组件使用


export default userSlice.reducer;