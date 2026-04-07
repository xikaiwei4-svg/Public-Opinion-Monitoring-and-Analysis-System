import http from 'http';

const server = http.createServer((req, res) => {
    // 设置CORS头
    res.writeHead(200, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });

    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.end();
        return;
    }

    // 根据不同的URL路径返回不同的模拟数据
    if (req.url === '/api/ping') {
        res.end(JSON.stringify({ status: 'ok', message: '服务运行正常' }));
    } 
    else if (req.url.startsWith('/api/舆情/list')) {
        const mockOpinions = {
            code: 200,
            data: {
                items: [
                    {
                        id: '1',
                        content: '今天学校食堂的饭菜质量有所提升，同学们都很满意！',
                        source: '微博',
                        publish_time: new Date().toISOString(),
                        sentiment: 0.8,
                        keywords: ['食堂', '饭菜质量'],
                        url: 'https://weibo.com/example1',
                        views: 1200,
                        likes: 89,
                        comments: 23
                    },
                    {
                        id: '2',
                        content: '图书馆的座位太紧张了，希望学校能够扩建一下。',
                        source: '微信公众号',
                        publish_time: new Date().toISOString(),
                        sentiment: -0.3,
                        keywords: ['图书馆', '座位'],
                        url: 'https://mp.weixin.qq.com/example2',
                        views: 2300,
                        likes: 156,
                        comments: 67
                    }
                ],
                total: 2,
                page: 1,
                page_size: 10
            },
            message: '查询成功'
        };
        res.end(JSON.stringify(mockOpinions));
    }
    else if (req.url.startsWith('/api/热点/话题/list')) {
        const mockHotTopics = {
            code: 200,
            data: [
                { id: '1', topic: '食堂饭菜质量提升', heat_score: 95, sentiment: 0.7 },
                { id: '2', topic: '图书馆座位紧张', heat_score: 88, sentiment: -0.4 },
                { id: '3', topic: '校园安全管理', heat_score: 76, sentiment: 0.2 }
            ],
            message: '查询成功'
        };
        res.end(JSON.stringify(mockHotTopics));
    }
    else if (req.url.startsWith('/api/趋势/analysis')) {
        const mockTrendData = {
            code: 200,
            data: {
                trend_data: [
                    { date: '2023-09-25', positive_count: 23, negative_count: 5, neutral_count: 12 },
                    { date: '2023-09-26', positive_count: 28, negative_count: 7, neutral_count: 15 },
                    { date: '2023-09-27', positive_count: 32, negative_count: 6, neutral_count: 18 }
                ],
                keyword: null,
                time_range: '2023-09-01 至 2023-09-30'
            },
            message: '查询成功'
        };
        res.end(JSON.stringify(mockTrendData));
    }
    else {
        res.end(JSON.stringify({ code: 404, message: 'Not Found' }));
    }
});

// 启动服务器
const PORT = 8000;
server.listen(PORT, () => {
    console.log(`Mock API Server running on http://localhost:${PORT}`);
});