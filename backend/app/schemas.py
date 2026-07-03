"""
Pydantic schemas - 请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==================== 对话相关 ====================

class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，用于关联对话历史")
    user_id: Optional[str] = Field(None, description="用户ID")

class ChatResponse(BaseModel):
    """对话响应"""
    response: str = Field(..., description="AI回复")
    session_id: str = Field(..., description="会话ID")
    message_id: int = Field(..., description="消息ID")
    token_count: int = Field(0, description="Token消耗")
    response_time: float = Field(0, description="响应时间(秒)")
    sources: Optional[List[str]] = Field(None, description="参考的知识库条目")

class MessageHistory(BaseModel):
    """历史消息"""
    id: int
    user_message: str
    ai_response: Optional[str]
    is_ai_response: bool
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationHistory(BaseModel):
    """会话历史"""
    session_id: str
    messages: List[MessageHistory]
    total: int

# ==================== 知识库相关 ====================

class KnowledgeBaseCreate(BaseModel):
    """创建知识库条目"""
    category: str = Field("general", description="分类: general, product, faq, policy")
    question: str = Field(..., min_length=1, description="问题")
    answer: str = Field(..., min_length=1, description="回答")
    keywords: Optional[str] = Field(None, description="关键词，逗号分隔")
    priority: int = Field(0, description="优先级")

class KnowledgeBaseUpdate(BaseModel):
    """更新知识库条目"""
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    keywords: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: int
    category: str
    question: str
    answer: str
    keywords: Optional[str]
    priority: int
    is_active: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class KnowledgeImport(BaseModel):
    """批量导入"""
    items: List[KnowledgeBaseCreate]

# ==================== 配置相关 ====================

class AIConfigUpdate(BaseModel):
    """AI配置更新"""
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    reply_style: Optional[str] = None  # friendly, professional, casual
    auto_reply: Optional[bool] = None
    transfer_threshold: Optional[int] = Field(None, ge=0, le=10)

class AIConfigResponse(BaseModel):
    """AI配置响应"""
    system_prompt: str
    temperature: float
    max_tokens: int
    reply_style: str
    auto_reply: bool
    transfer_threshold: int

# ==================== 统计相关 ====================

class DailyStatsResponse(BaseModel):
    """每日统计响应"""
    date: str
    total_conversations: int
    total_messages: int
    ai_handled: int
    human_handled: int
    avg_rating: float
    avg_response_time: float
    token_usage: int

class OverallStats(BaseModel):
    """总体统计"""
    total_conversations: int
    total_messages: int
    total_token_usage: int
    avg_rating: float
    avg_response_time: float
    knowledge_count: int
    today_conversations: int
    today_messages: int

class StatsChartData(BaseModel):
    """图表数据"""
    dates: List[str]
    conversations: List[int]
    messages: List[int]
    token_usage: List[int]

# ==================== 通用响应 ====================

class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    message: str
    data: Optional[dict] = None

class PageResponse(BaseModel):
    """分页响应"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
