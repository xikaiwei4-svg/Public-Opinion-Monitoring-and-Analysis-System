# -*- coding: utf-8 -*-

"""认证路由  基于MySQL数据库"""

from fastapi import APIRouter, HTTPException, Depends

from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import jwt, os, hashlib, logging

from typing import Optional

from dotenv import load_dotenv

load_dotenv()



from db.mysql_config import get_db

from models.mysql_models import User as UserModel



logger = logging.getLogger(__name__)



auth_router = APIRouter(prefix="/api/auth", tags=["认证"])



SECRET_KEY = os.getenv("SECRET_KEY", "campus-opinion-secret-key-2026")

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)





def hash_password(password: str) -> str:

    return hashlib.sha256(password.encode()).hexdigest()





def verify_password(password: str, hashed: str) -> bool:

    return hash_password(password) == hashed





def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)





def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    if token:

        try:

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user_id = payload.get("sub")

            if user_id:

                user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()

                if user:

                    return user

        except (jwt.PyJWTError, ValueError):

            pass

    # 未登录返回匿名用户

    return None





def ensure_db_admin(db: Session):

    """确保默认管理员存在"""

    admin = db.query(UserModel).filter(UserModel.username == "admin").first()

    if not admin:

        admin = UserModel(

            username="admin", email="admin@campus.edu",

            password_hash=hash_password("admin123"),

            role="admin", is_active=True, created_at=datetime.now()

        )

        db.add(admin)

        db.commit()





#  登录 

@auth_router.post("/login")

async def login(data: dict, db: Session = Depends(get_db)):

    ensure_db_admin(db)

    username = data.get("username", "")

    password = data.get("password", "")

    user = db.query(UserModel).filter(UserModel.username == username).first()

    if not user or not verify_password(password, user.password_hash):

        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:

        raise HTTPException(status_code=403, detail="账户已被禁用")

    user.last_login = datetime.now()

    db.commit()

    token = create_token({"sub": str(user.id)})

    return {

        "code": 200, "message": "登录成功",

        "data": {"token": token, "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

    }





#  获取当前用户 

@auth_router.get("/me")

async def me(user=Depends(get_current_user)):

    if not user:

        raise HTTPException(status_code=401, detail="未登录")

    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}





#  登出 

@auth_router.post("/logout")

async def logout():

    return {"code": 200, "message": "登出成功"}





#  注册 

@auth_router.post("/register")

async def register(data: dict, db: Session = Depends(get_db)):

    username = data.get("username", "").strip()

    password = data.get("password", "").strip()

    email = data.get("email", "").strip()

    if not username or not password:

        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    if len(password) < 6:

        raise HTTPException(status_code=400, detail="密码至少6位")

    existing = db.query(UserModel).filter(UserModel.username == username).first()

    if existing:

        raise HTTPException(status_code=400, detail="用户名已存在")

    user = UserModel(

        username=username, email=email,

        password_hash=hash_password(password),

        role="user", is_active=True, created_at=datetime.now()

    )

    db.add(user)

    db.commit()

    return {"code": 200, "message": "注册成功", "data": {"id": user.id, "username": user.username}}





#  用户列表 

@auth_router.get("/users")

async def users(page: int = 1, page_size: int = 10, user=Depends(get_current_user), db: Session = Depends(get_db)):

    if not user or user.role != "admin":

        raise HTTPException(status_code=403, detail="需要管理员权限")

    total = db.query(UserModel).count()

    items = db.query(UserModel).offset((page - 1) * page_size).limit(page_size).all()

    return {

        "code": 200,

        "data": {"items": [{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active, "created_at": u.created_at.isoformat() if u.created_at else None} for u in items], "total": total, "page": page, "page_size": page_size},

        "message": "查询成功"

    }





#  删除用户 

@auth_router.delete("/users/{user_id}")

async def delete_user(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):

    if not user or user.role != "admin":

        raise HTTPException(status_code=403, detail="需要管理员权限")

    if user.id == user_id:

        raise HTTPException(status_code=400, detail="不能删除自己")

    u = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not u:

        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(u)

    db.commit()

    return {"code": 200, "message": "删除成功"}

