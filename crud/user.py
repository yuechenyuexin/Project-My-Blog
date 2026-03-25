from datetime import timedelta, datetime, UTC
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from models.user import User, UserToken
from utils.jwt_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_refresh_token,
    verify_access_token
)
from schemas.user import UserCreateRequest


# -------------------------- 基础CRUD --------------------------
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[Dict[str, Any]]:
    """根据用户ID查询用户（返回字典，隐藏密码）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        return None

    # 转换为字典，排除密码字段
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "bio": user.bio,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名查询用户（返回ORM对象，含密码，仅内部使用）"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


# -------------------------- 注册/登录 --------------------------
async def create_user(db: AsyncSession, user_in: UserCreateRequest) -> User:
    """创建新用户（注册）"""
    # 1. 校验用户名是否已存在
    existing_user = await get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 2. 校验手机号（若传）是否已存在
    if user_in.phone:
        result = await db.execute(select(User).where(User.phone == user_in.phone))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已存在"
            )

    # 3. 密码加密 + 创建用户
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        password=hashed_password,
        nickname=user_in.nickname or user_in.username,  # 昵称默认等于用户名
        gender=user_in.gender or "unknown",
        bio=user_in.bio or "这个人很懒什么都没写",
        phone=user_in.phone,
        avatar=user_in.avatar or "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Dict[str, Any]:
    """用户登录认证：验证密码 + 生成Token + 存储Token"""
    # 1. 查询用户
    user = await get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 2. 验证密码
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 3. 生成JWT Token
    # 访问Token（30分钟）
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # 载荷存储用户ID（核心）
        # "sub"：JWT 标准里的保留字段，全称 subject（主题 / 主体），专门用来标识「这个 token 属于谁」
        # 这里用它来存用户 ID，意思是：「这个 token 是给 ID 为 user.id 的用户颁发的」。
        expires_delta=access_token_expires
    )

    # 刷新Token（7天，专门用来续期）
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 4. 清理该用户旧Token + 存储新Token
    await db.execute(delete(UserToken).where(UserToken.user_id == user.id))
    token_expires_at = datetime.now(UTC) + access_token_expires
    db_token = UserToken(
        user_id=user.id,
        token=access_token,
        expires_at=token_expires_at
    )
    db.add(db_token)
    await db.commit()

    # 5. 构造返回数据（隐藏密码）
    user_info = await get_user_by_id(db, user_id=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # 【新加】
        "token_type": "bearer",
        "user_info": user_info
    }


async def refresh_access_token(db: AsyncSession, refresh_token: str):
    """
    用Refresh Token换取新的Access Token
    """
    # 1. 验证Refresh Token是否合法
    payload = verify_access_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    # 2. 检查用户是否存在
    user = await get_user_by_id(db, user_id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 3. 生成新的Access Token
    new_access_token = create_access_token(data={"sub": user_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# -------------------------- 更新/删除 --------------------------
# 更新
async def update_user_info(
        db: AsyncSession,
        user_id: int,
        user_update: Dict[str, Any]
) -> Dict[str, Any]:
    """更新用户信息（仅更新传参字段）"""
    # 1. 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 2. 校验手机号（若更新）是否重复
    if "phone" in user_update and user_update["phone"]:
        result = await db.execute(
            select(User).where(User.phone == user_update["phone"], User.id != user_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被其他用户使用"
            )

    # 3. 仅更新允许的字段（避免恶意更新密码等敏感字段）
    allowed_fields = ["nickname", "avatar", "gender", "bio", "phone"]
    for field in allowed_fields:
        if field in user_update and user_update[field] is not None:
            setattr(user, field, user_update[field])

    await db.commit()
    await db.refresh(user)

    # 4. 返回更新后的用户信息
    return await get_user_by_id(db, user_id=user_id)


# 登出
async def logout_user(db: AsyncSession, user_id: int) -> None:
    """用户登出：删除该用户所有Token"""
    result = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    if not result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无有效登录Token"
        )

    await db.execute(delete(UserToken).where(UserToken.user_id == user_id))
    await db.commit()

