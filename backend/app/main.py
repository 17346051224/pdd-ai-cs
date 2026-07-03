"""
拼多多AI售前客服系统 - 后端应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, knowledge, config, stats
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="拼多多AI售前客服系统",
    description="基于DeepSeek的智能客服系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(config.router, prefix="/api/config", tags=["配置"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计"])

@app.get("/")
async def root():
    return {"message": "拼多多AI售前客服系统 API", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "pdd-ai-cs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
