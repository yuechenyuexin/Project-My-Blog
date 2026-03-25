import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from models.article import Article
from vector_store import add_article_to_vector_db
from config.db_config import ASYNC_DATABASE_URL


async def sync_all_articles():
    """同步数据库中所有文章到向量库"""
    # 1. 创建异步数据库会话
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=True,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )
    async with AsyncSession(async_engine) as session:
        # 2. 查询所有文章
        result = await session.execute(Article.__table__.select())
        articles = result.mappings().all()  # 转换为字典列表

        # 3. 批量同步到向量库
        total = len(articles)
        print(f"开始同步 {total} 篇文章到向量库...")

        # 看看谁不符合 chroma 的格式
        # for idx, article in enumerate(articles):
        #     print("=== 文章 {} 所有字段类型 ===".format(idx))
        #     for k, v in article.items():
        #         print(f"{k}: {type(v)}")  # 看哪个是 <class 'datetime.datetime'>

        for idx, article in enumerate(articles):    # datetime 对象是chroma不认的
            # 把 datetime 对象转成 ISO 格式字符串（兼容 Chroma）
            processed_article = dict(article)
            # 处理时间字段（不变）
            for time_key in ["created_at", "updated_at", "publish_time"]:
                if time_key in processed_article and processed_article[time_key]:
                    processed_article[time_key] = processed_article[time_key].isoformat()
            # 作者不能为空，不然也会报错，不然只能用下面的代码了
            # # 处理 author_name：如果是对象就转字符串，否则直接保留
            # if "author" in processed_article and processed_article["author"] is not None:
            #     # 情况1：author 是 User 对象，取 username 作为 author_name
            #     processed_article["author_name"] = processed_article["author"].username
            #     # 情况2：如果 author 本身就是字符串，直接用：processed_article["author_name"] = processed_article["author"]
            # else:
            #     processed_article["author_name"] = "未知作者"  # 兜底

            add_article_to_vector_db(processed_article)

            if (idx + 1) % 10 == 0:
                print(f"已同步 {idx + 1}/{total} 篇")

        print(f"同步完成！共同步 {total} 篇文章")


if __name__ == "__main__":
    # 运行同步脚本
    asyncio.run(sync_all_articles())