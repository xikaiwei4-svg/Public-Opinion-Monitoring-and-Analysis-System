"""pytest 共享 fixtures"""
import os
import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# 将项目根目录加入路径（使 backend 模块可导入）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def app():
    """导入 FastAPI 应用"""
    from main import app
    return app


@pytest.fixture(scope="session")
def client(app) -> Generator[TestClient, None, None]:
    """创建 TestClient（模拟 HTTP 请求，不用启动服务器）"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def anyio_backend():
    """pytest-asyncio 需要的后端配置"""
    return "asyncio"
