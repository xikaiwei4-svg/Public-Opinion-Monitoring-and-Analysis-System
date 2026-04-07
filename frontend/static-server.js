import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取当前文件的目录路径
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 支持的MIME类型
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'application/javascript',
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

// 创建HTTP服务器
const server = http.createServer((req, res) => {
    console.log(`Request for ${req.url} received`);

    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 确定请求的文件路径，如果是根路径则返回index.html
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index.html';
    }

    // 将相对路径转换为绝对路径
    const absolutePath = path.join(__dirname, filePath);

    // 检查文件是否存在
    fs.exists(absolutePath, (exists) => {
        if (!exists) {
            // 如果文件不存在，返回404错误
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 Not Found</h1>');
            return;
        }

        // 如果是目录，则查找目录中的index.html
        if (fs.statSync(absolutePath).isDirectory()) {
            filePath = path.join(filePath, 'index.html');
        }

        // 读取文件并返回给客户端
        fs.readFile(absolutePath, (err, content) => {
            if (err) {
                res.writeHead(500);
                res.end(`Error: ${err.code}..`);
            } else {
                // 设置正确的MIME类型
                const extname = String(path.extname(filePath)).toLowerCase();
                const contentType = mimeTypes[extname] || 'application/octet-stream';

                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content, 'utf-8');
            }
        });
    });
});

// 启动服务器
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Static File Server running on http://localhost:${PORT}`);
    console.log(`Mock API Server running on http://localhost:8000`);
    console.log(`请在浏览器中访问 http://localhost:${PORT} 查看前端页面`);
});