from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Literal, Any
from datetime import datetime


# -------------------------- 基础模型（复用字段） --------------------------
class UserBase(BaseModel):
    """用户基础模型（公共字段）"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="用户昵称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")    # 手机号用 str，这是行业铁律
    gender: Optional[Literal["male", "female", "unknown"]] = Field(None, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    # 通用模板，为了兼容「登录、修改资料、查询用户」所有场景，所以 username 设为 Optional（可选）。

# -------------------------- 请求模型 --------------------------
class UserCreateRequest(UserBase):
    """用户注册请求模型"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名（必填）"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        pattern=r"^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~`]*$",  # 核心正则
        description="密码：只能是 大小写字母+数字+常规英文符号，禁止中文/中文符号"
    )
    phone: str = Field(
        ...,
        min_length=11,
        max_length=11,
        pattern=r"^1[3-9]\d{9}$",
        description="手机号（必填）"
    )
    # 是注册专用模板，注册时用户名必须填，所以重新定义 username，把它从「可选」改成「必填」！
    # 子类重写的字段，会直接覆盖父类的同名字段    子类没重写的字段，直接继承父类的规则   其他字段可填可不填，不填也能注册成功!
    # 继承是为了复用字段，重复写字段是为了把可选改成必填，用户注册只需要填用户名和密码就够了！

class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名（必填）")
    password: str = Field(..., description="密码（必填）")

class UserUpdateRequest(UserBase):
    """用户信息更新请求模型（仅更新传参字段）"""
    pass




# -------------------------- 响应模型 --------------------------
class UserResponse(UserBase):
    """用户信息响应模型（隐藏密码）"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 兼容ORM模型转Pydantic（核心配置）
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """登录返回Token模型"""
    access_token: str = Field(..., description="JWT访问令牌（有效期30分钟，用于接口鉴权）")
    refresh_token: str = Field(..., description="JWT刷新令牌（有效期7天，用于续期访问令牌）")
    token_type: str = Field("bearer", description="令牌类型（固定为bearer）")
    user_info: UserResponse = Field(..., description="用户基础信息")

class CommonResponse(BaseModel):
    """通用响应模型（如注册/登出/更新）"""
    detail: str = Field(..., description="响应信息")
    data: Optional[Any] = Field(None, description="附加数据")


