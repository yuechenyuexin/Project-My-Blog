from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, Dict

from crud import get_user_by_id
from models import User
from models.article import Article
from schemas.article import ArticleCreate, ArticleUpdate
from vector_store import add_article_to_vector_db, delete_article_from_vector_db




async def get_article_by_id(db: AsyncSession, article_id: int) -> Optional[Dict]:
    """根据文章ID查询文章详情（返回字典）"""
    article = await db.get(Article, article_id)
    if not article:
        return None
    return {
        "id": article.id,
        "title": article.title,
        "description": article.description,
        "content": article.content,
        "image": article.image,
        "views": article.views,
        "category_id": article.category_id,
        "author_id": article.author_id,
        "author": article.author,
        "created_at": article.created_at,
        "updated_at": article.updated_at
    }


# ====================== 文章列表（可按分类筛选） ======================
async def get_article_list(
    db: AsyncSession,
    category_id: int | None = None,
    page: int = 1,
    size: int = 10
):
    # 总数
    stmt_count = select(func.count(Article.id))
    if category_id:
        stmt_count = stmt_count.where(Article.category_id == category_id)
    total = await db.scalar(stmt_count)

    # 列表
    stmt = select(Article)
    if category_id:
        stmt = stmt.where(Article.category_id == category_id)
    stmt = stmt.order_by(Article.created_at.desc()).limit(size).offset((page - 1) * size)

    result = await db.execute(stmt)
    articles = result.scalars().all()

    return {
        "total": total or 0,
        "items": articles
        # 这里就是ORM 对象 → Pydantic 响应的体现，以为路由的response_model里面有
        # from_attributes = True
    }

# ====================== 单篇文章 + 浏览量 +1 ======================
async def get_article_detail(db: AsyncSession, article_id: int):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 浏览量 +1
    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(views=Article.views + 1)
    )
    await db.commit()
    await db.refresh(article)

    return article
    # 这里就是ORM 对象 → Pydantic 响应的体现，以为路由的response_model里面有
    # from_attributes = True

# ====================== 创建文章 ======================
async def create_article(db: AsyncSession, article_in: ArticleCreate, author_id: int):
    result = await db.execute(select(User).where(User.id == author_id))
    author = result.scalars().first()
    article = Article(
        title=article_in.title,
        description=article_in.description,
        content=article_in.content,
        image=article_in.image,
        category_id=article_in.category_id,
        author = author.username,
        author_id=author_id,
        views=0
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)

    # 同步到向量库
    add_article_to_vector_db({
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "category_id": article.category_id,
        "author_id": article.author_id,
        "author": author.username
    })

    return article

# ====================== 更新文章（仅作者） ======================
async def update_article(
    db: AsyncSession,
    article_id: int,
    article_in: ArticleUpdate,
    current_user_id: int
):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    if article.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权限修改他人文章")

    data = article_in.dict(exclude_unset=True)   # 仅更新上传修改的内容
    for k, v in data.items():   # 修改的内容在data中呈现 {“title": "新标题"}
        setattr(article, k, v)  # k 是 title 是字典的键，v是新标题 是值  article.title = 新标题

    await db.commit()
    await db.refresh(article)

    # 更新向量库（先删旧的，再加新的）
    add_article_to_vector_db({
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "category_id": article.category_id,
        "author_id": article.author_id,
        "author": article.username
    })

    return article

# ====================== 删除文章（仅作者） ======================
async def delete_article(db: AsyncSession, article_id: int, current_user_id: int):
    article = await db.get(Article, article_id)
    # 按主键 ID 找出那篇文章，把它变成一个 Python 对象，方便接下来修改 / 删除 / 校验
    # 比select简单方便，适合直接查找主键
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    if article.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权限删除他人文章")

    await db.delete(article)
    await db.commit()

    # 从向量库删除
    delete_article_from_vector_db(article_id)

    return {"detail": "删除成功"}