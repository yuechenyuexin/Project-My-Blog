from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category  # 你的分类模型路径
from schemas.category import CategoryCreate, CategoryListResponse

# 查询分类列表（分页）
async def get_category_list(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
):
    # 统计总数  这里统计的是文章分类的总数，比如科技、生活等等，统计的是种类的个数，而不是种类及其文章
    count_stmt = select(func.count(Category.id))
    total = await db.scalar(count_stmt)

    # 查询列表
    stmt = select(Category).order_by(
        Category.sort_order.asc(),
        Category.created_at.desc()
    ).limit(size).offset((page-1)*size)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    return {
        "total": total or 0,
        "items": categories
    }


# 创建分类
async def create_category(
    db: AsyncSession,
    category_data: CategoryCreate
):
    # 数据转换
    db_category = Category(**category_data.model_dump())
    # 写入数据库
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category





