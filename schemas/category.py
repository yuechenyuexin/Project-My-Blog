from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 基础字段
class CategoryBase(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="分类名称")
    sort_order: Optional[int] = Field(0, description="排序号，越小越靠前")

# 创建分类（请求体）
class CategoryCreate(CategoryBase):
    name: str  # 名称必填

# 分类响应（返回给前端）
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 分页列表响应
class CategoryListResponse(BaseModel):
    total: int
    items: list[CategoryResponse]