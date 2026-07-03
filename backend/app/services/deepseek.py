"""
DeepSeek AI 服务
"""
import httpx
import json
import time
from typing import List, Dict, Optional, Tuple
from app.config import config
from app.models import Knowledge
from sqlalchemy.orm import Session

class DeepSeekService:
    """DeepSeek API 调用服务"""
    
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_base = config.DEEPSEEK_API_BASE
        self.model = config.DEEPSEEK_MODEL
        self.system_prompt = config.DEFAULT_SYSTEM_PROMPT
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
    
    def _build_knowledge_context(self, db: Session, query: str) -> str:
        """根据查询构建知识库上下文"""
        # 简单的关键词匹配
        keywords = query.replace("?", "").replace("？", "").split()
        
        # 查找相关知识库条目
        relevant_knowledge = db.query(Knowledge).filter(
            Knowledge.is_active == True
        ).all()
        
        # 计算相关性
        scored = []
        for k in relevant_knowledge:
            score = 0
            # 关键词匹配
            if k.keywords:
                for kw in keywords:
                    if kw.lower() in k.keywords.lower():
                        score += 3
            # 问题匹配
            for kw in keywords:
                if kw.lower() in k.question.lower():
                    score += 2
            # 回答匹配
            for kw in keywords:
                if kw.lower() in k.answer.lower():
                    score += 1
            # 优先级加成
            score += k.priority * 0.1
            
            if score > 0:
                scored.append((score, k))
        
        # 按分数排序，取前5条
        scored.sort(key=lambda x: x[0], reverse=True)
        top_knowledge = scored[:5]
        
        if top_knowledge:
            context = "\n\n【参考知识库】\n"
            for _, k in top_knowledge:
                context += f"Q: {k.question}\nA: {k.answer}\n\n"
            return context
        return ""
    
    def chat(
        self, 
        message: str, 
        history: List[Dict[str, str]] = None,
        db: Session = None,
        session_id: str = None
    ) -> Tuple[str, int, float, List[str]]:
        """
        发送对话请求
        
        Returns:
            (响应内容, token消耗, 响应时间, 参考来源)
        """
        start_time = time.time()
        
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加知识库上下文
        if db:
            knowledge_context = self._build_knowledge_context(db, message)
            if knowledge_context:
                # 将知识库上下文添加到系统提示中
                messages[0]["content"] += knowledge_context
        
        # 添加历史对话
        if history:
            for h in history[-10:]:  # 限制最近10条
                messages.append({"role": "user", "content": h.get("user", "")})
                if h.get("assistant"):
                    messages.append({"role": "assistant", "content": h.get("assistant")})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 调用API
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # 计算token（估算）
                    prompt_tokens = sum(len(m["content"]) // 4 for m in messages)
                    completion_tokens = len(content) // 4
                    total_tokens = prompt_tokens + completion_tokens
                    
                    response_time = time.time() - start_time
                    
                    return content, total_tokens, response_time, []
                else:
                    error_detail = response.text
                    raise Exception(f"API调用失败: {response.status_code} - {error_detail}")
                    
        except httpx.ConnectError:
            raise Exception(f"无法连接到DeepSeek API，请检查网络连接")
        except Exception as e:
            raise Exception(f"API调用错误: {str(e)}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试API连接"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "你好"}],
                        "max_tokens": 10
                    }
                )
                
                if response.status_code == 200:
                    return True, "API连接正常"
                else:
                    return False, f"API返回错误: {response.status_code}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

# 全局服务实例
deepseek_service = DeepSeekService()
