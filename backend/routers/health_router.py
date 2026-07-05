# -*- coding: utf-8 -*-

"""

健康检查端点  供 Docker healthcheck 和外部监控工具使用

无需认证即可访问

"""

from fastapi import APIRouter

from datetime import datetime, timezone

from typing import Dict, Any

import os

import logging



logger = logging.getLogger(__name__)



router = APIRouter(

    prefix="/api/health",

    tags=["健康检查"],

)





@router.get("")

async def liveness_check() -> Dict[str, Any]:

    """

    存活检查（Liveness） 最轻量



    Docker healthcheck 用此端点判断进程是否活着。

    只要 FastAPI 进程运行就返回 200。

    """

    return {

        "status": "ok",

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "service": "campus-opinion-backend",

        "version": os.getenv("APP_VERSION", "2.0.0"),

    }





@router.get("/ready")

async def readiness_check() -> Dict[str, Any]:

    """

    就绪检查（Readiness） 查依赖服务



    检查 MySQL 和 Redis 是否连通，两个都通才返回 200。

    有一个不通则返回 503，并在 detail 中说明是哪个服务异常。

    """

    checks = {"mysql": "unknown", "redis": "unknown"}

    all_ok = True



    #  检查 MySQL 

    try:

        from db.mysql_config import SessionLocal

        from sqlalchemy import text



        db = SessionLocal()

        result = db.execute(text("SELECT 1")).fetchone()

        if result and result[0] == 1:

            checks["mysql"] = "ok"

        else:

            checks["mysql"] = "unexpected_result"

            all_ok = False

        db.close()

    except Exception as e:

        checks["mysql"] = f"error: {str(e)}"

        all_ok = False

        logger.warning(f"MySQL 健康检查失败: {e}")



    #  检查 Redis 

    try:

        from utils.redis_cache import redis_cache



        if redis_cache.available:

            checks["redis"] = "ok"

        else:

            checks["redis"] = "not_available"

            all_ok = False

    except Exception as e:

        checks["redis"] = f"error: {str(e)}"

        all_ok = False

        logger.warning(f"Redis 健康检查失败: {e}")



    from fastapi.responses import JSONResponse



    result = {

        "status": "ready" if all_ok else "degraded",

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "checks": checks,

    }



    if all_ok:

        return result

    else:

        return JSONResponse(status_code=503, content={

            **result,

            "detail": "依赖服务异常，详见 checks 字段",

        })

