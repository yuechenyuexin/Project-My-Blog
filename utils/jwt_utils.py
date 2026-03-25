from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime, timedelta, UTC
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any


# 加载环境变量
load_dotenv()

# -------------------------- 密码加密配置 --------------------------
pwd_context = PasswordHash((BcryptHasher(),))

# -------------------------- JWT配置 --------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
# 这里JWT_ACCESS_TOKEN_EXPIRE_MINUTES优先 .env 文件里面的时间


# -------------------------- 密码操作函数 --------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# -------------------------- JWT操作函数 --------------------------
def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
) -> str:
    """生成JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 加入过期时间（JWT标准字段）
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """验证JWT令牌，返回载荷（无效/过期返回None）"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # jwt.decode() 会一次做后面三件事 解密 验签 验有效期
        return payload
    except ExpiredSignatureError:
        # 令牌过期
        return None
    except JWTError:
        # 令牌无效（签名错误/格式错误等）
        return None


# ===================== 【新加】刷新Token配置 =====================
# 刷新Token有效期（7天，可自己改）
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))


def create_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
) -> str:
    """生成Refresh Token（有效期长，用于续期）"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    # 用同一个密钥，不同用途
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt