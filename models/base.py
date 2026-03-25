from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime

# 所有模型的公共抽象基类（复用创建/更新时间字段）
class Base(DeclarativeBase):
    __abstract__ = True  # 标记为抽象基类，不生成数据库表

    # 公共创建时间字段：所有表自动继承
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,  # 无括号：每次创建数据时取当前时间（核心修正）
        comment="创建时间"
    )
    # 公共更新时间字段：所有表自动继承，更新时自动刷新
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,  # 更新操作时自动更新该字段
        comment="更新时间"
    )

