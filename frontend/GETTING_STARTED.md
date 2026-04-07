# 项目运行指南

## 重要提示
当前系统中的node.exe不包含完整的npm，因此需要安装完整的Node.js环境才能让代码正常运行。

## 安装步骤
1. 访问 Node.js 官方网站: https://nodejs.org/zh-cn/download/
2. 下载并安装适合您系统的LTS版本 (推荐18.x或20.x版本)
3. 安装完成后，打开命令提示符
4. 导航到项目的frontend目录:
   cd c:UsersweiDesktopproject1rontend
5. 运行以下命令安装依赖:
   npm install
6. 构建项目:
   npm run build
7. 启动开发服务器:
   npm run dev

## 验证安装
安装完成后，您可以运行以下命令验证Node.js和npm是否正确安装:
- node --version
- npm --version

## 项目说明
这是一个校园舆情分析系统的前端项目，基于React + TypeScript + Vite构建。

## 问题原因
当前项目目录中的node.exe文件只是Node.js的运行时部分，缺少完整的npm包管理器和相关组件。
要成功运行现代前端项目，必须安装完整的Node.js环境。