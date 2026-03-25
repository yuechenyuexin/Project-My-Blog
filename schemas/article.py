from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 基础字段
class ArticleBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None)
    image: Optional[str] = Field(None, max_length=255)
    category_id: Optional[int] = Field(None)

# 创建文章请求
class ArticleCreate(ArticleBase):
    title: str
    content: str
    category_id: int

# 更新文章请求
class ArticleUpdate(ArticleBase):
    pass

# 文章详情响应
class ArticleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: str
    image: Optional[str]
    views: int
    category_id: Optional[int]
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    # 这里就是我们是说的 from_attributes 返回时 ORM 对象 → Pydantic 响应的体现
    # 路由最后的返回，也就是crud操作完成得到的orm对象后就能利用这个自动转换后返回

# 列表分页响应
class ArticleListResponse(BaseModel):
    total: int
    items: list[ArticleResponse]