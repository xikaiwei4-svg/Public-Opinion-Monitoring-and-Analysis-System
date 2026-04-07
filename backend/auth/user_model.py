# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    id: str
    username: str
    password: str  # 在实际生产环境中，密码应该是加密存储的
    email: str
    role: str
    status: str = "active"
    created_at: datetime
    last_login: Optional[datetime] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    permissions: List[str] = []


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role: str = "user"
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    code: int
    data: dict
    message: str


class ApiResponse(BaseModel):
    code: int
    data: Optional[dict] = None
    message: str