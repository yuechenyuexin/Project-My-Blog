from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from config.db_config import get_db
from routers import user_router, category_router, article_router
from utils.exceptions import register_exception_handler
import asyncio
from sync_articles_to_vector import sync_all_articles

# 👇 读取环境变量，判断当前是「开发」还是「生产」环境
# 默认是开发环境（development），生产环境部署时设置 ENV=production
env = os.getenv("ENV", "development")

# 创建 FastAPI 实例，根据环境决定是否开启 Swagger
app = FastAPI(
    title="个人博客系统 API",
    version="0.1.0",
    # 👇 核心：生产环境关闭 Swagger 文档
    description="基于 FastAPI + MySQL 实现的博客接口",
    docs_url=None if env == "production" else "/docs",   # 关闭 /docs
    redoc_url=None if env == "production" else "/redoc" # 关闭 /redoc（另一种文档页面）
)

# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境替换为前端域名（如["http://localhost:8080"]）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常
register_exception_handler(app)

# 启动时同步现有文章到向量库（仅首次运行需要，后续可注释）
# @app.on_event("startup")
# async def startup_event():
#     print("项目启动中，开始同步文章到向量库...")
#     await sync_all_articles()
#     print("文章向量同步完成！")


@app.get("/test-db")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    return {"message": "数据库链接成功", "db_status": "正常"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(user_router)
app.include_router(category_router)
app.include_router(article_router)


@app.get("/", summary="健康检查")
async def root():
    return {"code": 200, "msg": "服务运行正常", "data": None}