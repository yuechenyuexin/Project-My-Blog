# scripts/create_tables.py
import asyncio
from config.db_config import async_engine  # 导入你的异步引擎
from models import Base  # 直接导入 models 包下的 Base
# Python 会自动找到 models 包，加载 __init__.py，拿到里面导出的 Base

# 异步创建所有表的核心函数
async def create_all_tables():
    # 异步引擎需要用connect()上下文，且create_all要指定bind
    async with async_engine.begin() as conn:
        # 创建所有继承Base的模型对应的表（如果表已存在则跳过）
        await conn.run_sync(Base.metadata.create_all)
    print("所有数据表创建成功！")

# 执行脚本
if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(create_all_tables())