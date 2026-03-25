from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from config.db_config import get_db
from schemas import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    TokenResponse,
    CommonResponse,
    ApiResponse
)
from crud import (
    create_user,
    authenticate_user,
    refresh_access_token,
    update_user_info,
    logout_user
)
from dependencies.auth import get_current_user


# -------------------------- 用户模块 -------------------------- #

router = APIRouter(
    prefix="/api/users",
    tags=["用户模块"],
    responses={404: {"description": "Not Found"}},
)

@router.post(
    "/register",
    summary="用户注册",
    status_code=status.HTTP_201_CREATED,
    # 告诉所有人「注册 = 创建用户成功」，注册 = 创建用户，就必须返回 201
    # 前端看到 201，不用看返回内容，就知道「用户创建成功了」
    response_model=ApiResponse[CommonResponse]
    # 强制统一格式 自动校验 前端零沟通成本 团队协作
)
async def register(
    user_data: UserCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """用户注册接口（无需登录）"""
    user = await create_user(db, user_data)
    return ApiResponse(msg="注册成功", data={"user_id": user.id, "username": user.username})


@router.post(
    "/login",
    summary="用户登录",
    response_model=ApiResponse[TokenResponse]
)
async def login(
    login_in: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """用户登录接口"""
    data = await authenticate_user(db, login_in.username, login_in.password)
    return ApiResponse(msg="登录成功", data=data)



@router.post(
    "/refresh-token",
    summary="刷新Access Token（续期）",
    description="用Refresh Token换取新的Access Token，用户无感知续期"
)
async def refresh_token(
    refreshing_token: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    data = await refresh_access_token(db, refreshing_token)
    return ApiResponse(msg="刷新续期Token", data=data)


# -------------------------- 需登录的接口 --------------------------
# docs测试不了的接口，用powershell
@router.get(
    "/me",
    summary="获取当前登录用户信息",
    response_model=ApiResponse[UserResponse]
)
async def get_my_info(
    current_user: Annotated[dict, Depends(get_current_user)]
    # Annotated 括号内第一个位置说明的是要传入的是什么类型的参数
    # 第二个位置代表，这个参数是从哪来的
):
    """获取当前登录用户信息（需登录）"""
    return ApiResponse(data=current_user)


# docs测试不了的接口，用powershell
@router.put(
    "/me",
    summary="更新当前登录用户信息",
    response_model=ApiResponse[CommonResponse]
)
async def update_my_info(
    user_update: UserUpdateRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """更新当前登录用户信息（需登录）"""
    data = await update_user_info(
        db,
        user_id=current_user["id"],
        # 注意上面能发现get_current_user返回的内容是字典
        # 从auth的get_current_user到crud的get_user_by_id的return的是字典了
        user_update=user_update.dict(exclude_unset=True)  # 仅更新传参字段
        # 这里是 .dict把uer_update这个Pydantic类型变成了字典
        # 等同于 user_update.model_dump(exclude_unset=True)
    )
    return ApiResponse(msg="更新成功", data=data)



@router.post(
    "/logout",
    summary="用户登出",
    response_model=ApiResponse[CommonResponse]
)
async def logout(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """用户登出（需登录，删除Token）"""
    await logout_user(db, user_id=current_user["id"])
    return ApiResponse(msg="登出成功")





