"""
数据统计路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.models import Conversation, DailyStats, Knowledge
from app.schemas import DailyStatsResponse, OverallStats, StatsChartData

router = APIRouter()

@router.get("/overall", response_model=OverallStats)
async def get_overall_stats(db: Session = Depends(get_db)):
    """
    获取总体统计数据
    """
    # 总对话数
    total_conversations = db.query(func.count(func.distinct(Conversation.session_id))).scalar() or 0
    
    # 总消息数
    total_messages = db.query(func.count(Conversation.id)).scalar() or 0
    
    # Token总消耗
    total_token_usage = db.query(func.sum(Conversation.token_count)).scalar() or 0
    
    # 平均评分
    avg_rating = db.query(func.avg(Conversation.rating)).filter(
        Conversation.rating.isnot(None)
    ).scalar() or 0
    
    # 平均响应时间
    avg_response_time = db.query(func.avg(Conversation.response_time)).scalar() or 0
    
    # 知识库条目数
    knowledge_count = db.query(func.count(Knowledge.id)).scalar() or 0
    
    # 今日数据
    today = datetime.now().strftime("%Y-%m-%d")
    today_stats = db.query(DailyStats).filter(DailyStats.date == today).first()
    
    return OverallStats(
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_token_usage=total_token_usage,
        avg_rating=round(avg_rating, 2),
        avg_response_time=round(avg_response_time, 2),
        knowledge_count=knowledge_count,
        today_conversations=today_stats.total_conversations if today_stats else 0,
        today_messages=today_stats.total_messages if today_stats else 0
    )

@router.get("/daily", response_model=List[DailyStatsResponse])
async def get_daily_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    获取每日统计数据
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    stats = db.query(DailyStats).filter(
        DailyStats.date >= start_date.strftime("%Y-%m-%d")
    ).order_by(DailyStats.date.asc()).all()
    
    # 如果没有数据，生成模拟数据用于展示
    if not stats:
        result = []
        for i in range(days):
            date = (end_date - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
            result.append(DailyStatsResponse(
                date=date,
                total_conversations=0,
                total_messages=0,
                ai_handled=0,
                human_handled=0,
                avg_rating=0,
                avg_response_time=0,
                token_usage=0
            ))
        return result
    
    return [
        DailyStatsResponse(
            date=s.date,
            total_conversations=s.total_conversations,
            total_messages=s.total_messages,
            ai_handled=s.ai_handled,
            human_handled=s.human_handled,
            avg_rating=s.avg_rating,
            avg_response_time=s.avg_response_time,
            token_usage=s.token_usage
        )
        for s in stats
    ]

@router.get("/chart")
async def get_chart_data(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    获取图表数据
    """
    end_date = datetime.now()
    dates = []
    conversations = []
    messages = []
    token_usage = []
    
    for i in range(days):
        date = (end_date - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        stats = db.query(DailyStats).filter(DailyStats.date == date).first()
        
        dates.append(date)
        conversations.append(stats.total_conversations if stats else 0)
        messages.append(stats.total_messages if stats else 0)
        token_usage.append(stats.token_usage if stats else 0)
    
    return StatsChartData(
        dates=dates,
        conversations=conversations,
        messages=messages,
        token_usage=token_usage
    )

@router.get("/hourly")
async def get_hourly_stats(
    date: str = Query(None, description="日期，格式YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取小时级统计数据
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 模拟小时数据
    # 实际实现需要按小时聚合
    hours = list(range(24))
    counts = [0] * 24
    
    # 模拟高峰时段
    for h in [9, 10, 11, 14, 15, 16, 19, 20, 21]:
        import random
        counts[h] = random.randint(10, 50)
    
    return {
        "date": date,
        "hours": hours,
        "counts": counts
    }

@router.get("/rating-distribution")
async def get_rating_distribution(db: Session = Depends(get_db)):
    """
    获取评分分布
    """
    distribution = []
    for rating in range(1, 6):
        count = db.query(func.count(Conversation.id)).filter(
            Conversation.rating == rating
        ).scalar() or 0
        distribution.append({"rating": rating, "count": count})
    
    return distribution
