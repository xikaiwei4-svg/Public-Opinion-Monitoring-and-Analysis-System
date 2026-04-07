const express = require('express');
const router = express.Router();

// 模拟用户数据
const mockUsers = [
  {
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    name: '管理员',
    avatar: '/api/avatar/admin.png',
    role: 'admin',
    department: '信息中心',
    position: '系统管理员',
    permissions: ['all'],
    created_at: '2023-01-01T00:00:00',
    updated_at: '2023-01-01T00:00:00'
  },
  {
    id: '2',
    username: 'user1',
    email: 'user1@example.com',
    name: '张三',
    avatar: '/api/avatar/user1.png',
    role: 'user',
    department: '学生处',
    position: '科员',
    permissions: ['view'],
    created_at: '2023-01-02T00:00:00',
    updated_at: '2023-01-02T00:00:00'
  },
  {
    id: '3',
    username: 'user2',
    email: 'user2@example.com',
    name: '李四',
    avatar: '/api/avatar/user2.png',
    role: 'user',
    department: '教务处',
    position: '科员',
    permissions: ['view'],
    created_at: '2023-01-03T00:00:00',
    updated_at: '2023-01-03T00:00:00'
  },
  {
    id: '4',
    username: 'user3',
    email: 'user3@example.com',
    name: '王五',
    avatar: '/api/avatar/user3.png',
    role: 'user',
    department: '科研处',
    position: '科员',
    permissions: ['view'],
    created_at: '2023-01-04T00:00:00',
    updated_at: '2023-01-04T00:00:00'
  }
];

// 获取用户列表
router.get('/list', (req, res) => {
  const { page = 1, page_size = 10, keyword, role, department } = req.query;
  
  // 筛选数据
  let filteredData = [...mockUsers];
  
  if (keyword) {
    filteredData = filteredData.filter(item => 
      item.username.includes(keyword) || 
      item.name.includes(keyword) || 
      item.email.includes(keyword)
    );
  }
  
  if (role) {
    filteredData = filteredData.filter(item => item.role === role);
  }
  
  if (department) {
    filteredData = filteredData.filter(item => item.department === department);
  }
  
  // 分页
  const total = filteredData.length;
  const startIndex = (page - 1) * page_size;
  const endIndex = startIndex + parseInt(page_size);
  const paginatedData = filteredData.slice(startIndex, endIndex);
  
  res.json({
    items: paginatedData,
    total: total,
    page: parseInt(page),
    page_size: parseInt(page_size)
  });
});

// 获取用户详情
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const user = mockUsers.find(item => item.id === id);
  
  if (!user) {
    return res.status(404).json({
      code: 404,
      message: '用户不存在'
    });
  }
  
  res.json(user);
});

module.exports = router;
