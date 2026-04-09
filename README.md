# 校园舆情监测与热点话题分析系统

一套基于大数据技术的校园舆情实时监测系统，支持多平台数据采集、情感分析、热点话题挖掘及可视化展示。

## 🚀 项目特点

- **实时监测**: 多平台数据实时采集和分析
- **情感分析**: 自动识别舆情情感倾向（正面/负面/中性）
- **热点挖掘**: 智能识别校园热点话题和趋势
- **可视化展示**: 丰富的图表展示和数据可视化
- **数据管理**: 完善的数据库管理和爬虫任务调度

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: MySQL + SQLAlchemy ORM
- **任务调度**: Celery + Redis
- **数据处理**: Pandas, NumPy

### 前端
- **框架**: React 18 + TypeScript
- **状态管理**: Redux Toolkit
- **UI组件**: Ant Design
- **构建工具**: Vite
- **可视化**: ECharts

## 📁 项目结构

```
project1/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI主入口
│   ├── db/                 # 数据库配置
│   │   ├── mysql_config.py # MySQL连接配置
│   │   └── ...
│   ├── models/             # 数据模型
│   │   ├── mysql_models.py # MySQL模型定义
│   │   └── ...
│   ├── routers/            # API路由
│   │   ├── mysql_database_router.py  # 数据库管理API
│   │   ├── sentiment_router.py       # 情感分析API
│   │   └── ...
│   ├── tasks/              # 异步任务
│   │   └── crawler_tasks.py # 爬虫任务
│   └── requirements.txt    # Python依赖
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   │   ├── Dashboard.tsx         # 数据仪表盘
│   │   │   ├── OpinionListPage.tsx   # 舆情列表
│   │   │   ├── DatabaseManagePage.tsx # 数据库管理
│   │   │   └── ...
│   │   ├── components/    # 通用组件
│   │   ├── store/         # Redux状态管理
│   │   ├── api/           # API接口封装
│   │   └── App.tsx        # 应用入口
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
│
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd project1
```

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 backend/db/mysql_config.py 中的数据库连接信息

# 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

后端服务将在 http://localhost:8001 运行
API文档: http://localhost:8001/docs

### 3. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 运行

## 📊 核心功能

### 1. 舆情监测
- 实时展示最新舆情数据
- 支持关键词搜索和筛选
- 情感倾向分析（正面/负面/中性）
- 数据来源平台分布

### 2. 热点话题
- 自动识别热点话题
- 话题趋势分析
- 相关舆情关联

### 3. 数据可视化
- 舆情趋势图
- 平台分布饼图
- 情感分析柱状图
- 热点词云

### 4. 数据库管理
- 数据库状态监控
- 数据集合管理
- 爬虫任务管理
- 数据导入导出

## 🔧 配置说明

### 数据库配置
编辑 `backend/db/mysql_config.py`:

```python
class MySQLSettings(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "your_username"
    MYSQL_PASSWORD: str = "your_password"
    MYSQL_DATABASE: str = "campus_opinion"
```

### 前端代理配置
编辑 `frontend/vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true
    }
  }
}
```

## 📝 API接口

### 舆情数据接口
- `GET /api/database/opinions` - 获取舆情列表
- `GET /api/database/opinions/{id}` - 获取舆情详情
- `POST /api/database/opinions` - 创建舆情数据
- `DELETE /api/database/opinions/{id}` - 删除舆情数据

### 情感分析接口
- `GET /api/sentiment/analyze/{opinion_id}` - 分析单条舆情情感
- `POST /api/sentiment/batch_analyze` - 批量分析情感
- `GET /api/sentiment/statistics` - 获取情感统计

### 热点话题接口
- `GET /api/hot_topics` - 获取热点话题列表
- `GET /api/hot_topics/{id}` - 获取话题详情
- `GET /api/hot_topics/trend` - 获取话题趋势

## 🎯 项目亮点

1. **前后端分离架构**: 使用FastAPI + React实现前后端分离
2. **响应式设计**: 支持PC端和移动端适配
3. **组件化开发**: 使用React组件化思想，提高代码复用性
4. **状态管理**: 使用Redux Toolkit进行全局状态管理
5. **类型安全**: 使用TypeScript进行类型约束
6. **数据可视化**: 使用ECharts实现丰富的图表展示
7. **性能优化**: 实现数据分页加载，优化大数据量展示性能

## 📈 项目成果

- 成功采集并分析3000+条校园相关舆情数据
- 实现实时数据更新和可视化展示
- 系统响应时间 < 500ms
- 支持并发访问

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

- 姓名: [Your Name]
- 邮箱: [Your Email]
- GitHub: [Your GitHub]

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [React](https://reactjs.org/) - 前端框架
- [Ant Design](https://ant.design/) - UI组件库
- [ECharts](https://echarts.apache.org/) - 可视化库
