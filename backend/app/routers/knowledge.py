"""
知识库路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Knowledge
from app.schemas import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    KnowledgeImport
)

router = APIRouter()

@router.get("", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_list(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取知识库列表
    """
    query = db.query(Knowledge)
    
    if category:
        query = query.filter(Knowledge.category == category)
    
    if keyword:
        query = query.filter(
            (Knowledge.question.contains(keyword)) | 
            (Knowledge.answer.contains(keyword)) |
            (Knowledge.keywords.contains(keyword))
        )
    
    if is_active is not None:
        query = query.filter(Knowledge.is_active == is_active)
    
    total = query.count()
    items = query.order_by(Knowledge.priority.desc(), Knowledge.updated_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return items

@router.get("/{knowledge_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    """
    获取单条知识库
    """
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    return knowledge

@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge(
    data: KnowledgeBaseCreate, 
    db: Session = Depends(get_db)
):
    """
    创建知识库条目
    """
    knowledge = Knowledge(
        category=data.category,
        question=data.question,
        answer=data.answer,
        keywords=data.keywords,
        priority=data.priority
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge

@router.post("/import")
async def import_knowledge(
    data: KnowledgeImport, 
    db: Session = Depends(get_db)
):
    """
    批量导入知识库
    """
    imported = 0
    for item in data.items:
        knowledge = Knowledge(
            category=item.category,
            question=item.question,
            answer=item.answer,
            keywords=item.keywords,
            priority=item.priority
        )
        db.add(knowledge)
        imported += 1
    
    db.commit()
    return {"success": True, "imported": imported}

@router.put("/{knowledge_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge(
    knowledge_id: int,
    data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """
    更新知识库条目
    """
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(knowledge, key, value)
    
    db.commit()
    db.refresh(knowledge)
    return knowledge

@router.delete("/{knowledge_id}")
async def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    """
    删除知识库条目
    """
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    db.delete(knowledge)
    db.commit()
    
    return {"success": True, "message": "删除成功"}

@router.post("/toggle/{knowledge_id}")
async def toggle_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    """
    启用/禁用知识库条目
    """
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    knowledge.is_active = not knowledge.is_active
    db.commit()
    
    return {
        "success": True, 
        "message": "已启用" if knowledge.is_active else "已禁用",
        "is_active": knowledge.is_active
    }

@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """
    获取所有分类
    """
    from sqlalchemy import func
    categories = db.query(
        Knowledge.category,
        func.count(Knowledge.id).label("count")
    ).group_by(Knowledge.category).all()
    
    return [{"category": c.category, "count": c.count} for c in categories]

@router.get("/search/similar")
async def search_similar(
    query: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    相似问题搜索
    """
    # 简单的关键词匹配
    keywords = query.replace("?", "").replace("？", "").split()
    
    all_knowledge = db.query(Knowledge).filter(Knowledge.is_active == True).all()
    
    results = []
    for k in all_knowledge:
        score = 0
        for kw in keywords:
            if kw.lower() in k.question.lower():
                score += 3
            if k.keywords:
                if kw.lower() in k.keywords.lower():
                    score += 2
            if kw.lower() in k.answer.lower():
                score += 1
        
        if score > 0:
            results.append({
                "id": k.id,
                "question": k.question,
                "answer": k.answer,
                "score": score
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
