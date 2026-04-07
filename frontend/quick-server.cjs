// 简单的静态文件服务器
const http = require('http');
const fs = require('fs');
const path = require('path');
const port = 3000;

// 创建服务器
const server = http.createServer((req, res) => {
  // 确定要提供的文件路径
  let filePath = '.' + req.url;
  if (filePath === './') {
    filePath = './ultra-simple-react-test.html'; // 默认页面
  }

  // 获取文件扩展名
  const extname = String(path.extname(filePath)).toLowerCase();

  // 映射文件扩展名到MIME类型
  const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.woff': 'application/font-woff',
    '.ttf': 'application/font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.otf': 'application/font-otf',
    '.wasm': 'application/wasm'
  };

  const contentType = mimeTypes[extname] || 'application/octet-stream';

  // 读取文件并发送响应
  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        // 文件未找到
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1><p>页面不存在</p>');
      } else {
        // 服务器错误
        res.writeHead(500);
        res.end('Sorry, check with the site admin for error: ' + error.code + ' ..\n');
      }
    } else {
      // 成功读取文件
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

// 启动服务器
server.listen(port, () => {
  console.log(`\n✅ 简易静态服务器已启动`);
  console.log(`请在浏览器中访问 http://localhost:${port}`);
  console.log('\n注意：这只是一个临时服务器，可以查看静态页面。');
  console.log('要运行完整的React项目，请安装完整的Node.js环境并执行npm install和npm run dev。');
  console.log('\n按Ctrl+C停止服务器');
});

// 处理关闭信号
process.on('SIGINT', () => {
  console.log('\n服务器正在关闭...');
  server.close(() => {
    console.log('服务器已停止');
    process.exit(0);
  });
});