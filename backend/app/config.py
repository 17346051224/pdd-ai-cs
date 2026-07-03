"""
系统配置管理
"""
import os
from typing import Optional

class Config:
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/pdd_cs.db")
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 系统配置
    SYSTEM_NAME: str = os.getenv("SYSTEM_NAME", "拼多多AI售前客服")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 前端配置
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # 默认AI人设
    DEFAULT_SYSTEM_PROMPT: str = """你是一个专业的拼多多店铺售前客服助手。你的职责是：
1. 热情友好地接待顾客，解答关于商品的疑问
2. 了解顾客需求，推荐合适的商品
3. 介绍商品的特点、规格、价格、优惠活动
4. 解答物流、发货、售后等问题
5. 引导顾客下单，提供优质的购物体验
6. 遇到无法回答的问题，礼貌地引导顾客联系人工客服

请使用友好、专业的语气与顾客交流。"""
    
    # 拼多多开放平台配置（预留）
    PDD_CLIENT_ID: Optional[str] = os.getenv("PDD_CLIENT_ID")
    PDD_CLIENT_SECRET: Optional[str] = os.getenv("PDD_CLIENT_SECRET")
    PDD_ACCESS_TOKEN: Optional[str] = os.getenv("PDD_ACCESS_TOKEN")

config = Config()
