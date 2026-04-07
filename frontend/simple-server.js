import http from 'http';
import fs from 'fs';
import path from 'path';

// 确保端口未被占用
const PORT = 3000;

// 创建服务器
const server = http.createServer((req, res) => {
    // 设置CORS头，允许所有来源
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // 处理请求
    let filePath = '.' + req.url;
    
    // 如果请求根路径，返回simple-index.html
    if (filePath === './') {
        filePath = './simple-index.html';
    }

    const extname = path.extname(filePath);
    let contentType = 'text/html';
    
    // 设置内容类型
    switch (extname) {
        case '.js':
            contentType = 'text/javascript';
            break;
        case '.css':
            contentType = 'text/css';
            break;
        case '.json':
            contentType = 'application/json';
            break;
        case '.png':
            contentType = 'image/png';
            break;
        case '.jpg':
            contentType = 'image/jpg';
            break;
        case '.gif':
            contentType = 'image/gif';
            break;
        case '.svg':
            contentType = 'image/svg+xml';
            break;
    }

    // 读取文件并发送响应
    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                // 文件不存在，返回404
                res.writeHead(404);
                res.end('404 Not Found');
            } else {
                // 其他错误，返回500
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`);
            }
        } else {
            // 文件存在，发送文件内容
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
            
            // 记录请求日志
            console.log(`Request for ${req.url} received and served successfully`);
        }
    });
});

// 启动服务器
server.listen(PORT, () => {
    console.log(`Static File Server running on http://localhost:${PORT}`);
    console.log('Mock API Server running on http://localhost:8000');
    console.log('请在浏览器中访问 http://localhost:3000 查看前端页面');
});