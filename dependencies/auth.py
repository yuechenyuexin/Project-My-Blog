from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

from config.db_config import get_db
from utils.jwt_utils import verify_access_token
from crud.user import get_user_by_id

# -------------------------- OAuth2认证方案 --------------------------
# 定义token获取方式：请求头 Authorization: Bearer <token>
# 从请求头里自动捞 Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# -------------------------- 依赖函数：获取当前登录用户 --------------------------
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """
    核心依赖：验证token有效性，并返回当前登录用户信息
    - 无token/无效token/过期token → 401未授权
    - token有效但用户不存在 → 404未找到
    """
    # 1. 验证token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的令牌或令牌已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token)
    if not payload:
        raise credentials_exception

    # 2. 从token载荷中获取用户ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 3. 查询用户信息
    user = await get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


# -------------------------- 扩展：管理员权限校验（可选） --------------------------
async def get_current_admin_user(
        current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """
    管理员权限校验（示例：可根据实际需求扩展，如user表加is_admin字段）
    """
    # 这里仅为示例，实际需根据user表的is_admin字段判断
    # if not current_user.get("is_admin"):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="无管理员权限"
    #     )
    return current_user