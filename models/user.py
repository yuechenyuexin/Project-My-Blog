from typing import Optional
from datetime import datetime
from sqlalchemy import Index, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base  # 导入统一的抽象基类

class User(Base):
    """用户信息表 ORM 模型"""
    __tablename__ = "blog_user"  # 统一表名前缀：blog_ + 业务名（适配博客场景）

    # 索引配置：唯一索引确保用户名/手机号不重复
    __table_args__ = (
        Index('idx_blog_user_username_unique', "username", unique=True),
        Index('idx_blog_user_phone_unique', 'phone', unique=True)
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名（登录用）"
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码（建议加密存储）"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="用户昵称"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        default='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
        comment="头像URL"
    )
    gender: Mapped[str] = mapped_column(  # 去掉Optional：默认值保证非空
        Enum('male', 'female', 'unknown'),
        nullable=False,
        default="unknown",
        comment="性别（male/女female/未知unknown）"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        default="这个人很懒什么都没写",
        comment="个人简介"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        comment="手机号（可选）"
    )

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username}, nickname={self.nickname})>'


class UserToken(Base):
    """用户令牌表 ORM 模型（存储登录token）"""
    __tablename__ = "blog_user_token"  # 统一表名前缀

    # 索引配置：token唯一 + 用户ID外键索引（提升查询速度）
    __table_args__ = (
        Index('idx_blog_user_token_unique', 'token', unique=True),
        Index('fk_blog_user_token_user_idx', 'user_id')
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="令牌ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("blog_user.id"),  # 关联重构后的用户表名
        nullable=False,
        comment="关联用户ID"
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="登录令牌值"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="令牌过期时间"
    )

    def __repr__(self):
        return f'<UserToken(id={self.id}, user_id={self.user_id}, token="{self.token}")>'