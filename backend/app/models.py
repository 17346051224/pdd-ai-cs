"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Knowledge(Base):
    """知识库条目"""
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), default="general", index=True)  # general, product, faq, policy
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(String(500))  # 逗号分隔的关键词
    priority = Column(Integer, default=0)  # 优先级，数字越大优先级越高
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conversation(Base):
    """对话记录"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)  # 会话ID
    user_id = Column(String(100))  # 用户标识
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text)
    is_ai_response = Column(Boolean, default=True)
    rating = Column(Integer, nullable=True)  # 用户评分 1-5
    feedback = Column(Text)  # 用户反馈
    token_count = Column(Integer, default=0)  # token消耗
    response_time = Column(Float, default=0)  # 响应时间(秒)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class AIConfig(Base):
    """AI配置"""
    __tablename__ = "ai_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True)
    config_value = Column(Text)
    description = Column(String(500))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyStats(Base):
    """每日统计"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), unique=True, index=True)  # YYYY-MM-DD格式
    total_conversations = Column(Integer, default=0)  # 总对话数
    total_messages = Column(Integer, default=0)  # 总消息数
    ai_handled = Column(Integer, default=0)  # AI处理数
    human_handled = Column(Integer, default=0)  # 转人工数
    avg_rating = Column(Float, default=0)  # 平均评分
    avg_response_time = Column(Float, default=0)  # 平均响应时间
    token_usage = Column(Integer, default=0)  # Token消耗
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
