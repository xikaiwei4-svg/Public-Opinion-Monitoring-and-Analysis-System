import urllib.request

try:
    # 测试连接到前端服务器
    response = urllib.request.urlopen('http://localhost:8080/standalone-dashboard.html')
    print('前端服务器状态码:', response.status)
    
    # 测试连接到后端API
    backend_response = urllib.request.urlopen('http://localhost:8000/api/opinions/statistics')
    print('后端API状态码:', backend_response.status)
    
    print('服务器连接测试完成')
except Exception as e:
    print('连接测试失败:', str(e))