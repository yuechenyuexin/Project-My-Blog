from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from schemas import (
    CategoryListResponse,
    CategoryResponse,
    CategoryCreate,
    ApiResponse
)
from crud import (
    get_category_list,
    create_category
)
from routers.user import get_current_user

# 路由配置
router = APIRouter(
    prefix="/api/categories",
    tags=["分类模块"]
)


# 1. 查询分类列表
@router.get("", response_model=ApiResponse[CategoryListResponse], summary="获取分类列表")
async def list_categories(
    cc,       # 这个是没默认值的参数，不能放在下面两行有默认值参数后面
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
):
    data = await get_category_list(db=db, page=page, size=size)
    return ApiResponse(msg="查得分类", data=data)
    # 这里返回的是分类的总数，和各个分类按照顺序排列出来，而不是各个分类下面的文章数


# 2. 创建分类
@router.post("", response_model=ApiResponse[CategoryResponse], summary="创建分类")
async def create_new_category(
    category_data: CategoryCreate,                  # 没默认参数
    db: Annotated[AsyncSession, Depends(get_db)],    # 没默认参数
    current_user: Annotated[dict, Depends(get_current_user)]
):
    # 权限校验：只有用户名是「谌月夜」的用户才能创建分类
    if current_user.get("username") != "谌月夜":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限创建分类"
        )
    data = await create_category(db=db, category_data=category_data)
    return ApiResponse(msg="创建分类成功", data=data)









