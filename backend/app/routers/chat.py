"""
对话路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Conversation, AIConfig
from app.schemas import ChatRequest, ChatResponse, ConversationHistory, MessageHistory
from app.services.deepseek import deepseek_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    发送消息并获取AI回复
    """
    # 生成会话ID
    session_id = request.session_id or str(uuid.uuid4())
    
    # 获取历史对话
    history = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at.desc()).limit(10).all()
    
    # 构建历史消息列表
    history_list = []
    for h in reversed(history):
        if h.user_message:
            history_list.append({
                "user": h.user_message,
                "assistant": h.ai_response
            })
    
    # 获取AI配置
    ai_config = db.query(AIConfig).filter(
        AIConfig.config_key == "system_prompt"
    ).first()
    
    if ai_config and ai_config.config_value:
        deepseek_service.set_system_prompt(ai_config.config_value)
    
    # 调用DeepSeek
    try:
        response_text, token_count, response_time, sources = deepseek_service.chat(
            message=request.message,
            history=history_list,
            db=db,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 保存对话记录
    conversation = Conversation(
        session_id=session_id,
        user_id=request.user_id,
        user_message=request.message,
        ai_response=response_text,
        is_ai_response=True,
        token_count=token_count,
        response_time=response_time
    )
    db.add(conversation)
    
    # 更新每日统计
    today = datetime.now().strftime("%Y-%m-%d")
    from app.models import DailyStats
    stats = db.query(DailyStats).filter(DailyStats.date == today).first()
    if stats:
        stats.total_conversations += 1
        stats.total_messages += 2
        stats.token_usage += token_count
    else:
        stats = DailyStats(
            date=today,
            total_conversations=1,
            total_messages=2,
            token_usage=token_count
        )
        db.add(stats)
    
    db.commit()
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        message_id=conversation.id,
        token_count=token_count,
        response_time=response_time,
        sources=sources
    )

@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(session_id: str, db: Session = Depends(get_db)):
    """
    获取会话历史
    """
    messages = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at.asc()).all()
    
    return ConversationHistory(
        session_id=session_id,
        messages=[MessageHistory.model_validate(m) for m in messages],
        total=len(messages)
    )

@router.get("/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    """
    获取所有会话列表
    """
    from sqlalchemy import func, desc
    
    # 按session_id分组，获取每个会话的最新消息
    sessions = db.query(
        Conversation.session_id,
        func.max(Conversation.created_at).label("last_time"),
        func.count(Conversation.id).label("message_count"),
        Conversation.user_message.label("last_message")
    ).group_by(Conversation.session_id).order_by(
        desc("last_time")
    ).limit(50).all()
    
    return [
        {
            "session_id": s.session_id,
            "last_time": s.last_time.isoformat() if s.last_time else None,
            "message_count": s.message_count,
            "last_message": s.last_message
        }
        for s in sessions
    ]

@router.post("/rate/{message_id}")
async def rate_conversation(message_id: int, rating: int, feedback: str = None, db: Session = Depends(get_db)):
    """
    评价对话
    """
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")
    
    conversation = db.query(Conversation).filter(Conversation.id == message_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    
    conversation.rating = rating
    conversation.feedback = feedback
    db.commit()
    
    # 更新平均评分
    today = datetime.now().strftime("%Y-%m-%d")
    from app.models import DailyStats
    stats = db.query(DailyStats).filter(DailyStats.date == today).first()
    if stats:
        # 重新计算平均评分
        avg_rating = db.query(func.avg(Conversation.rating)).filter(
            Conversation.rating.isnot(None)
        ).scalar() or 0
        stats.avg_rating = round(avg_rating, 2)
        db.commit()
    
    return {"success": True, "message": "评价成功"}
