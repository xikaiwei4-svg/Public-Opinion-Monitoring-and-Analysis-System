const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');

// 模拟用户数据
const mockUsers = [
  {
    id: '1',
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',
    name: '管理员',
    avatar: '/api/avatar/admin.png',
    role: 'admin',
    department: '信息中心',
    position: '系统管理员',
    permissions: ['all']
  },
  {
    id: '2',
    username: 'user',
    password: 'user123',
    email: 'user@example.com',
    name: '普通用户',
    avatar: '/api/avatar/user.png',
    role: 'user',
    department: '学生处',
    position: '科员',
    permissions: ['view']
  }
];

// 登录路由
router.post('/login', (req, res) => {
  const { username, password } = req.body;
  
  // 验证用户
  const user = mockUsers.find(u => u.username === username && u.password === password);
  
  if (!user) {
    return res.status(401).json({
      code: 401,
      message: '用户名或密码错误'
    });
  }
  
  // 生成JWT token
  const token = jwt.sign(
    { id: user.id, username: user.username, role: user.role },
    'your-secret-key', // 在实际应用中，应使用环境变量存储
    { expiresIn: '24h' }
  );
  
  // 返回用户信息和token
  res.json({
    token: token,
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      name: user.name,
      avatar: user.avatar,
      role: user.role,
      department: user.department,
      position: user.position,
      permissions: user.permissions
    }
  });
});

// 获取当前用户信息
router.get('/me', (req, res) => {
  // 在实际应用中，应从token中解析用户信息
  // 这里为了简化，直接返回默认用户
  const user = mockUsers[0];
  
  res.json({
    id: user.id,
    username: user.username,
    email: user.email,
    name: user.name,
    avatar: user.avatar,
    role: user.role,
    department: user.department,
    position: user.position,
    permissions: user.permissions
  });
});

module.exports = router;
