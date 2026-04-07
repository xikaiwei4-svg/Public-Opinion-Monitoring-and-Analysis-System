const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

// 导入路由
const authRoutes = require('./routes/auth');
const opinionRoutes = require('./routes/opinion');
const hotTopicRoutes = require('./routes/hotTopic');
const trendRoutes = require('./routes/trend');
const userRoutes = require('./routes/user');

const app = express();
const PORT = process.env.PORT || 8000;

// 中间件
app.use(cors({
  origin: 'http://localhost:3000', // 前端开发服务器地址
  credentials: true
}));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 健康检查
app.get('/api/ping', (req, res) => {
  res.json({ status: 'success', message: 'Server is running' });
});

// 路由
app.use('/api/auth', authRoutes);
app.use('/api/opinion', opinionRoutes);
app.use('/api/hot-topic', hotTopicRoutes);
app.use('/api/trend', trendRoutes);
app.use('/api/users', userRoutes);

// 404处理
app.use((req, res) => {
  res.status(404).json({ code: 404, message: 'Not Found' });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ code: 500, message: 'Internal Server Error' });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
