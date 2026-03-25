from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Index, ForeignKey, Text, DateTime
from datetime import datetime
from .base import Base  # 导入统一的抽象基类


class Article(Base):
    """博客文章表 ORM 模型"""
    __tablename__ = "blog_article"  # 适配博客场景：news → article

    # 索引配置：外键+高频查询字段索引
    __table_args__ = (
        Index('fk_blog_article_category_idx', 'category_id'),  # 分类ID外键索引
        Index('idx_blog_article_publish_time', 'publish_time')  # 发布时间索引
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="文章ID"
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="文章标题"
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        comment="文章简介/摘要"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="文章正文内容"
    )
    image: Mapped[str | None] = mapped_column(
        String(255),
        comment="文章封面图片URL"
    )
    author: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("blog_user.username"),
        nullable=False,
        comment="文章作者（可选，默认取用户昵称）"
    )
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("blog_user.id"),
        nullable=False,
        comment="关联作者ID"
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('blog_category.id'),  # 关联重构后的分类表名
        nullable=False,
        comment="关联分类ID"
    )
    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="文章浏览量"
    )
    publish_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="文章发布时间"
    )

    # 修正：__repr__ 缩进至类内部（核心语法修复）
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', views={self.views})>"