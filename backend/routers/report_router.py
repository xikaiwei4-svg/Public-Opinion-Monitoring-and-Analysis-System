# -*- coding: utf-8 -*-
"""报告 API —— 生成、列表、详情、删除、导出"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
from datetime import datetime

from db.mysql_config import SessionLocal
from models.report_model import Report

router = APIRouter(prefix="/api/report", tags=["智能报告"])


@router.post("/generate")
async def generate_report(background_tasks: BackgroundTasks, report_type: str = "weekly"):
    """异步生成报告（Agent 查询 + DeepSeek 生成）"""
    from services.report_agent import run_report_agent

    try:
        result = await run_report_agent(report_type)
        if not result:
            raise HTTPException(status_code=500, detail="报告生成失败，请检查 DeepSeek API Key 是否配置")
        return {"code": 200, "data": result, "message": "报告生成成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成异常: {str(e)}")


@router.get("/list")
async def list_reports(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    report_type: Optional[str] = None,
):
    """获取报告历史列表"""
    db = SessionLocal()
    try:
        q = db.query(Report)
        if report_type:
            q = q.filter(Report.report_type == report_type)
        total = q.count()
        items = q.order_by(Report.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
        return {
            "items": [r.to_dict() for r in items],
            "total": total,
            "page": page,
            "page_size": pageSize,
        }
    finally:
        db.close()


@router.get("/{report_id}")
async def get_report(report_id: int):
    """获取单份报告详情"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        return {"code": 200, "data": report.to_dict()}
    finally:
        db.close()


@router.post("/trace")
async def generate_trace_report(keyword: str):
    """生成事件脉络追踪报告"""
    from services.trace_agent import run_trace_agent
    try:
        result = await run_trace_agent(keyword)
        if not result:
            raise HTTPException(status_code=500, detail="脉络分析失败，请检查 API Key")
        return {"code": 200, "data": result, "message": "脉络分析完成"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脉络分析异常: {str(e)}")


@router.post("/monitor")
async def run_alert_monitor():
    """执行一次完整舆情巡检"""
    from services.alert_agent import run_alert_agent
    try:
        result = await run_alert_agent()
        if not result:
            raise HTTPException(status_code=500, detail="巡检失败，请检查 API Key")
        return {"code": 200, "data": result, "message": "巡检完成"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"巡检异常: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(report_id: int):
    """删除报告"""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        db.delete(report)
        db.commit()
        return {"code": 200, "message": "报告已删除"}
    except HTTPException:
        raise
    finally:
        db.close()
