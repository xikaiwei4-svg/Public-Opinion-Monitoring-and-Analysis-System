# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
import os
import logging
from typing import Dict, Optional, List

from .user_model import User, LoginRequest, LoginResponse, UserCreate, UserUpdate, ApiResponse

# 创建路由实例
auth_router = APIRouter(
    prefix="/api/auth",
    tags=["认证"],
    responses={404: {"description": "未找到"}},
)

# 模拟用户数据（在实际生产环境中，应该从数据库读取）
# 注意：在实际生产环境中，密码应该加密存储
MOCK_USERS = [
    {
        "id": "1",
        "username": "admin",
        "password": "admin123",  # 实际生产环境中应该是加密的密码
        "email": "admin@example.com",
        "role": "admin",
        "status": "active",
        "created_at": datetime.now(),
        "permissions": ["read", "write", "delete", "admin"],
        "department": "系统管理部",
        "position": "管理员"
    },
    {
        "id": "2",
        "username": "user",
        "password": "user123",  # 实际生产环境中应该是加密的密码
        "email": "user@example.com",
        "role": "user",
        "status": "active",
        "created_at": datetime.now(),
        "permissions": ["read", "write"],
        "department": "数据分析部",
        "position": "分析员"
    }
]

# 日志记录器
logger = logging.getLogger(__name__)

# 简单的JWT配置（强制要求环境变量，不使用不安全的默认值）
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.error("Environment variable SECRET_KEY not set; aborting startup for security.")
    raise RuntimeError("Environment variable SECRET_KEY must be set to a strong secret; do not use default weak values.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2密码持有者模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# 创建访问令牌
def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 验证令牌并获取用户信息
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证凭证")
        
        # 在实际生产环境中，应该从数据库查询用户
        user = next((u for u in MOCK_USERS if u["username"] == username), None)
        if user is None:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭证")


# 登录API端点
@auth_router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    # 在实际生产环境中，应该从数据库查询用户并验证密码
    user = next((u for u in MOCK_USERS if u["username"] == login_request.username), None)
    
    # 验证用户是否存在以及密码是否正确
    if not user or user["password"] != login_request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查用户状态
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="用户账户未激活")
    
    # 更新最后登录时间
    user["last_login"] = datetime.now()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # 准备返回数据，不包含密码
    user_data = user.copy()
    user_data.pop("password")
    
    return {
        "code": 200,
        "data": {
            "token": access_token,
            "user": user_data
        },
        "message": "登录成功"
    }


# 获取当前用户信息API端点
@auth_router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # 不包含密码的用户信息
    user_data = current_user.copy()
    user_data.pop("password")
    
    return {
        "code": 200,
        "data": user_data,
        "message": "查询成功"
    }


# 登出API端点
@auth_router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # 在实际生产环境中，可能需要实现令牌黑名单或其他登出机制
    # 这里简化处理，前端只需要删除本地存储的token即可
    return {
        "code": 200,
        "data": None,
        "message": "登出成功"
    }


# ==================== 用户管理API ====================

# 获取用户列表
@auth_router.get("/users")
async def get_users(
    page: int = 1,
    page_size: int = 10,
    role: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # 检查权限，只有管理员可以访问
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    
    # 过滤用户
    filtered_users = MOCK_USERS.copy()
    
    if role:
        filtered_users = [u for u in filtered_users if u.get("role") == role]
    
    if status:
        filtered_users = [u for u in filtered_users if u.get("status") == status]
    
    # 分页
    total = len(filtered_users)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_users = filtered_users[start_idx:end_idx]
    
    # 不包含密码
    users_data = []
    for user in paginated_users:
        user_data = user.copy()
        user_data.pop("password", None)
        users_data.append(user_data)
    
    return {
        "code": 200,
        "data": {
            "items": users_data,
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "message": "查询成功"
    }


# 获取单个用户
@auth_router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # 检查权限，只有管理员或用户自己可以访问
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不包含密码
    user_data = user.copy()
    user_data.pop("password", None)
    
    return {
        "code": 200,
        "data": user_data,
        "message": "查询成功"
    }


# 创建用户
@auth_router.post("/users")
async def create_user(
    user_create: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    # 检查权限，只有管理员可以创建用户
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    
    # 检查用户名是否已存在
    existing_user = next((u for u in MOCK_USERS if u["username"] == user_create.username), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    new_user = {
        "id": str(len(MOCK_USERS) + 1),
        "username": user_create.username,
        "password": user_create.password,  # 实际生产环境应该加密
        "email": user_create.email,
        "role": user_create.role,
        "status": "active",
        "created_at": datetime.now(),
        "phone": user_create.phone,
        "department": user_create.department,
        "position": user_create.position,
        "permissions": ["read", "write"] if user_create.role == "user" else ["read", "write", "delete", "admin"]
    }
    
    MOCK_USERS.append(new_user)
    
    # 不包含密码
    user_data = new_user.copy()
    user_data.pop("password")
    
    return {
        "code": 200,
        "data": user_data,
        "message": "用户创建成功"
    }


# 更新用户
@auth_router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    # 检查权限，只有管理员或用户自己可以更新
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 管理员可以修改更多字段，普通用户只能修改部分字段
    is_admin = current_user.get("role") == "admin"
    
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    if user_update.username is not None:
        # 检查用户名是否已被其他用户使用
        if user_update.username != user["username"]:
            existing_user = next((u for u in MOCK_USERS if u["username"] == user_update.username), None)
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")
        user["username"] = user_update.username
    
    if user_update.email is not None:
        user["email"] = user_update.email
    
    if is_admin:
        if user_update.role is not None:
            user["role"] = user_update.role
            user["permissions"] = ["read", "write"] if user_update.role == "user" else ["read", "write", "delete", "admin"]
        if user_update.status is not None:
            user["status"] = user_update.status
    
    if user_update.phone is not None:
        user["phone"] = user_update.phone
    
    if user_update.department is not None:
        user["department"] = user_update.department
    
    if user_update.position is not None:
        user["position"] = user_update.position
    
    # 不包含密码
    user_data = user.copy()
    user_data.pop("password")
    
    return {
        "code": 200,
        "data": user_data,
        "message": "用户更新成功"
    }


# 删除用户
@auth_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # 检查权限，只有管理员可以删除用户
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    
    # 不能删除自己
    if current_user.get("id") == user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的用户")
    
    user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 删除用户
    deleted_user = MOCK_USERS.pop(user_index)
    
    # 不包含密码
    user_data = deleted_user.copy()
    user_data.pop("password")
    
    return {
        "code": 200,
        "data": user_data,
        "message": "用户删除成功"
    }