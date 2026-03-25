# 导入必要模块（新增dotenv读取环境变量）
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from dotenv import load_dotenv
import os

# 加载.env文件的环境变量（优先加载，避免硬编码）
load_dotenv()

# 从环境变量读取数据库配置（安全且易修改）
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_CHARSET = os.getenv("DB_CHARSET")

# 拼接异步数据库URL（格式：mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=字符集）
ASYNC_DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_CHARSET}"

# 创建异步引擎（优化连接池参数，适配博客项目）
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# 创建异步会话工厂（核心：生成数据库会话的模板）
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# FastAPI依赖函数：提供数据库会话（每次请求独立会话，自动关闭）
async def get_db():
    async with AsyncSessionLocal() as session:  # 上下文管理器自动管理会话
        try:
            yield session
        finally:
            await session.close()














