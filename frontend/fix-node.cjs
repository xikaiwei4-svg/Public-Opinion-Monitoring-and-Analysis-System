// 简单的依赖管理助手脚本 (CommonJS格式)
const fs = require('fs');
const path = require('path');

console.log('正在准备Node.js环境...');

// 检查项目基本信息
const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
console.log(`项目名称: ${packageJson.name} v${packageJson.version}`);
console.log('这是一个React + TypeScript + Vite项目');

// 检查node.exe状态
console.log('Node.js版本:', process.version);

// 创建说明文件
const instructions = `# 项目运行指南

## 重要提示
当前系统中的node.exe不包含完整的npm，因此需要安装完整的Node.js环境才能让代码正常运行。

## 安装步骤
1. 访问 Node.js 官方网站: https://nodejs.org/zh-cn/download/
2. 下载并安装适合您系统的LTS版本 (推荐18.x或20.x版本)
3. 安装完成后，打开命令提示符
4. 导航到项目的frontend目录:
   cd c:\Users\wei\Desktop\project1\frontend
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
要成功运行现代前端项目，必须安装完整的Node.js环境。`;

fs.writeFileSync('./GETTING_STARTED.md', instructions);

console.log('\n✅ 环境检查完成！');
console.log('\n已创建GETTING_STARTED.md文件，其中包含详细的安装指南。');
console.log('\n主要问题: 您需要安装完整的Node.js环境才能运行此项目。');
console.log('当前的node.exe文件不包含完整的npm功能。');
console.log('\n请按照GETTING_STARTED.md中的步骤操作以成功运行项目。');
console.log('\n另外，我还为您创建了一个简单的测试服务器脚本，让您可以临时查看静态页面。');