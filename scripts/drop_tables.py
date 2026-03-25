import asyncio
from sqlalchemy import text  # 新增：用于执行外键约束的SQL语句
from config.db_config import async_engine  # 和create_tables.py保持一致
from models import Base  # 和create_tables.py保持一致

# 异步删除所有表的核心函数
async def drop_all_tables():
    async with async_engine.begin() as conn:
        # 1. 先关闭外键约束（避免删除表时因外键关联报错）
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        # 2. 删除所有继承自Base的表（和create_all对应，只是变成drop_all）
        await conn.run_sync(Base.metadata.drop_all)
        # 3. 恢复外键约束
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("所有数据表已删除成功！")

# 执行脚本（和create_tables.py完全一样的运行方式）
if __name__ == "__main__":
    asyncio.run(drop_all_tables())