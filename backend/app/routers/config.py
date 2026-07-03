"""
系统配置路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AIConfig
from app.schemas import AIConfigUpdate, AIConfigResponse
from app.config import config
from app.services.deepseek import deepseek_service

router = APIRouter()

# 默认配置值
DEFAULT_CONFIG = {
    "system_prompt": config.DEFAULT_SYSTEM_PROMPT,
    "temperature": 0.7,
    "max_tokens": 1000,
    "reply_style": "friendly",
    "auto_reply": True,
    "transfer_threshold": 3
}

@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config(db: Session = Depends(get_db)):
    """
    获取AI配置
    """
    result = {}
    
    # 从数据库读取配置
    configs = db.query(AIConfig).all()
    config_dict = {c.config_key: c.config_value for c in configs}
    
    # 合并默认配置
    for key, default_value in DEFAULT_CONFIG.items():
        if key in config_dict:
            try:
                if isinstance(default_value, bool):
                    result[key] = config_dict[key].lower() == "true"
                elif isinstance(default_value, float):
                    result[key] = float(config_dict[key])
                elif isinstance(default_value, int):
                    result[key] = int(config_dict[key])
                else:
                    result[key] = config_dict[key]
            except (ValueError, TypeError):
                result[key] = default_value
        else:
            result[key] = default_value
    
    return AIConfigResponse(**result)

@router.put("/ai", response_model=AIConfigResponse)
async def update_ai_config(
    data: AIConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    更新AI配置
    """
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        # 查找或创建配置
        config_obj = db.query(AIConfig).filter(
            AIConfig.config_key == key
        ).first()
        
        if config_obj:
            config_obj.config_value = str(value)
        else:
            config_obj = AIConfig(
                config_key=key,
                config_value=str(value),
                description=f"AI配置项: {key}"
            )
            db.add(config_obj)
    
    db.commit()
    
    # 如果更新了system_prompt，更新全局服务
    if data.system_prompt:
        deepseek_service.set_system_prompt(data.system_prompt)
    
    # 返回更新后的配置
    return await get_ai_config(db)

@router.get("/ai/test")
async def test_ai_connection(db: Session = Depends(get_db)):
    """
    测试AI连接
    """
    success, message = deepseek_service.test_connection()
    
    if success:
        return {"success": True, "message": message}
    else:
        return {"success": False, "message": message}

@router.get("/system/info")
async def get_system_info():
    """
    获取系统信息
    """
    return {
        "system_name": config.SYSTEM_NAME,
        "version": "1.0.0",
        "deepseek_model": config.DEEPSEEK_MODEL,
        "pdd_configured": bool(config.PDD_CLIENT_ID and config.PDD_CLIENT_SECRET),
        "features": {
            "deepseek": True,
            "pinduoduo": False,  # 等备案后启用
            "knowledge_base": True,
            "export": True
        }
    }

@router.get("/pdd/status")
async def get_pdd_status(db: Session = Depends(get_db)):
    """
    获取拼多多对接状态
    """
    from app.services.pdd import pdd_service
    
    if pdd_service.is_configured:
        return {
            "configured": True,
            "message": "拼多多API已配置",
            "features": ["订单查询", "商品同步", "消息收发"]
        }
    else:
        return {
            "configured": False,
            "message": "拼多多API未配置，请完成ICP备案后配置PDD_CLIENT_ID和PDD_CLIENT_SECRET",
            "features": []
        }
