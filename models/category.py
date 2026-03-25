from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, DateTime, func
from .base import Base  # 导入统一的抽象基类

# 分类表模型 → 运行项目会自动创建 categories 表
class Category(Base):
    """文章分类表 ORM 模型"""
    __tablename__ = "blog_category"  # 适配博客场景：去掉news前缀

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类ID"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="分类名称（如：技术、生活、随笔）"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="分类排序（数值越小越靠前）"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort_order={self.sort_order})>"
