from asyncio import to_thread

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from config.db_config import get_db
from dependencies.auth import get_current_user
from schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ApiResponse
)
from crud import (
    get_article_list,
    get_article_detail,
    create_article,
    update_article,
    delete_article
)
from vector_store import search_similar_articles
from crud.article import get_article_by_id  # 根据article_id查询文章详情

router = APIRouter(
    prefix="/api/articles",
    tags=["文章模块"]
)

# ======================== 文章搜索 ========================
@router.get("/search", response_model=ApiResponse)
async def search_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query(..., min_length=1, description="搜索关键词"),
    top_k: int = Query(10, ge=1, le=50, description="返回最相似的文章数量"),
    category_id: int | None = Query(None, description="按分类筛选")
):
    """
    语义搜索相似文章（公开接口，无需登录）
    :param db: 异步数据库会话，由 FastAPI 依赖注入自动提供
    :param query: 搜索关键词（如“机器学习”“Python教程”）
    :param top_k: 返回前N篇相似文章
    :param category_id: 可选，按分类筛选
    :return: 相似文章列表（含详情+相似度）
    """
    # 1. 语义搜索，获取相似文章ID列表
    similar_article_ids = await to_thread(
        search_similar_articles,
        query=query,
        top_k=top_k,
        category_id=category_id
    )

    # 2. 批量查询文章详情（根据article_id）
    article_details = []
    for item in similar_article_ids:
        article = await get_article_by_id(db, article_id=item["article_id"])
        if article:  # 避免向量库有但数据库已删除的情况
            article_details.append({
                "article": article,
                "similarity": item["similarity"]  # 相似度分数
            })

    # # 3. 按相似度降序排序
    # article_details.sort(key=lambda x: x["similarity"], reverse=True)

    return ApiResponse(
        msg="搜索成功",
        data={
            "total": len(article_details),
            "items": article_details
        }
    )



# ====================== 文章列表（公开） ======================
@router.get("", response_model=ApiResponse[ArticleListResponse])
async def list_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    data = await get_article_list(db, category_id=category_id, page=page, size=size)
    return ApiResponse(msg="查得文章", data=data)



# ====================== 文章详情（公开，浏览量+1） ======================
@router.get("/{article_id}", response_model=ApiResponse[ArticleResponse])
async def retrieve_article(
    db: Annotated[AsyncSession, Depends(get_db)],
    article_id: int
):
    data = await get_article_detail(db, article_id)
    return ApiResponse(data=data)



# ====================== 创建文章（需登录） ======================
@router.post("", response_model=ApiResponse[ArticleResponse])
async def create(
    db: Annotated[AsyncSession, Depends(get_db)],
    article_in: ArticleCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    data = await create_article(db, article_in, author_id=current_user["id"])
    return ApiResponse(msg="创建成功", data=data)


# ====================== 更新文章（仅作者） ======================
@router.put("/{article_id}", response_model=ApiResponse[ArticleResponse])
async def update(
    db: Annotated[AsyncSession, Depends(get_db)],
    article_id: int,
    article_in: ArticleUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    data = await update_article(db, article_id, article_in, current_user["id"])
    return ApiResponse(msg="更新文章成功", data=data)



# ====================== 删除文章（仅作者） ======================
@router.delete("/{article_id}")
async def remove(
    db: Annotated[AsyncSession, Depends(get_db)],
    article_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    data = await delete_article(db, article_id, current_user["id"])
    return ApiResponse(msg="删除文章成功")









