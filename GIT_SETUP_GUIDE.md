# Git 上传指南

## 📦 项目打包完成

项目已经准备好上传到GitHub/GitLab。以下是上传步骤：

## ✅ 已完成的工作

1. ✅ 创建 `.gitignore` 文件 - 排除不需要的文件
2. ✅ 创建 `README.md` 文件 - 项目说明文档
3. ✅ 检查并清理敏感信息 - 移除数据库密码等敏感数据
4. ✅ 创建 `.env.example` 文件 - 环境变量示例

## 🚀 上传到GitHub的步骤

### 1. 安装Git

如果还没有安装Git，请先下载安装：
- Windows: https://git-scm.com/download/win
- Mac: `brew install git`
- Linux: `sudo apt-get install git`

### 2. 配置Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 初始化Git仓库

在项目根目录下执行：

```bash
cd c:\Users\wei\Desktop\project1
git init
```

### 4. 添加文件到Git

```bash
# 添加所有文件
git add .

# 或者分步添加
git add README.md
git add .gitignore
git add backend/
git add frontend/
```

### 5. 提交代码

```bash
git commit -m "Initial commit: Campus Opinion Monitoring System

- Add backend with FastAPI and MySQL
- Add frontend with React and TypeScript
- Implement opinion monitoring and sentiment analysis
- Add data visualization with ECharts
- Support 3000+ opinion data processing"
```

### 6. 创建GitHub仓库

1. 登录GitHub: https://github.com
2. 点击右上角 "+" -> "New repository"
3. 填写仓库名称: `campus-opinion-monitoring`
4. 选择公开或私有
5. 不要初始化README（因为我们已经有了）
6. 点击 "Create repository"

### 7. 连接到远程仓库

```bash
# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/yourusername/campus-opinion-monitoring.git

# 推送到GitHub
git push -u origin main
```

如果默认分支是master：
```bash
git push -u origin master
```

### 8. 验证上传

访问你的GitHub仓库页面，确认代码已上传成功。

## 📁 项目结构说明

上传后，你的GitHub仓库将包含：

```
campus-opinion-monitoring/
├── .gitignore              # Git忽略文件配置
├── README.md               # 项目说明文档
├── GIT_SETUP_GUIDE.md      # 本指南
├── backend/                # 后端代码
│   ├── main.py
│   ├── db/
│   ├── models/
│   ├── routers/
│   ├── tasks/
│   ├── requirements.txt
│   └── .env.example        # 环境变量示例
│
└── frontend/               # 前端代码
    ├── src/
    ├── package.json
    └── vite.config.ts
```

## 🔒 安全注意事项

1. **不要上传敏感信息**:
   - 数据库密码
   - API密钥
   - 私钥文件
   - `.env` 文件（已添加到.gitignore）

2. **已保护的内容**:
   - ✅ Python虚拟环境 (`.venv/`)
   - ✅ Node模块 (`node_modules/`)
   - ✅ 编译缓存 (`__pycache__/`, `*.pyc`)
   - ✅ 日志文件 (`*.log`)
   - ✅ 环境变量文件 (`.env`)

## 📝 提交信息规范

建议的提交信息格式：

```
<type>: <subject>

<body>

<footer>
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: add sentiment analysis API

- Implement sentiment analysis using keyword matching
- Add batch processing support
- Update API documentation"
```

## 🌿 分支管理建议

```bash
# 创建开发分支
git checkout -b develop

# 创建功能分支
git checkout -b feature/sentiment-analysis

# 合并分支
git checkout main
git merge feature/sentiment-analysis
```

## 📊 项目统计

上传后，你可以在GitHub上看到：
- 代码行数统计
- 主要编程语言占比（Python + TypeScript）
- 提交历史
- 贡献者图表

## 🎯 后续优化建议

1. **添加LICENSE文件**: 选择开源许可证（如MIT）
2. **创建Issue模板**: 规范问题反馈
3. **添加CI/CD**: 使用GitHub Actions自动化测试和部署
4. **编写测试**: 添加单元测试和集成测试
5. **完善文档**: 添加API文档、部署文档等

## 🆘 常见问题

### Q1: 推送失败，提示权限错误
A: 检查是否配置了SSH密钥或使用HTTPS链接
```bash
# 使用HTTPS
git remote set-url origin https://github.com/username/repo.git

# 或使用SSH
git remote set-url origin git@github.com:username/repo.git
```

### Q2: 文件太大无法上传
A: 检查是否正确配置了.gitignore，确保没有上传node_modules等目录

### Q3: 如何更新代码
A: 修改文件后执行：
```bash
git add .
git commit -m "update: description"
git push
```

## 📞 需要帮助？

- GitHub文档: https://docs.github.com
- Git文档: https://git-scm.com/doc
- 遇到问题可以查看GitHub的Help页面

---

**祝你的项目获得更多Star！⭐**
