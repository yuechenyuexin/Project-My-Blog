from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

# 这里是通用字段输出
# schemas里面的模型还是能对前端展示例子和限制输出字段的