from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from schemas import ApiResponse

def register_exception_handler(app: FastAPI):
    # 处理 HTTPException
    # 装饰器：监听所有 HTTPException 类型的异常
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            # 🔥 关键：HTTP状态码强制返回200！
            # 前后端分离约定：前端不看HTTP状态码，只看你返回的code
            status_code=200,
            # 用 ApiResponse 包装异常信息
            content=ApiResponse(
                code=exc.status_code,
                msg=exc.detail,
                data=None
            ).dict()
            # ApiResponse 是 Pydantic 模型，不能直接返回给前端，必须用 .dict() 转成普通字典，才能变成 JSON
        )

    # 处理所有未知异常
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=200,
            content=ApiResponse(
                code=500,
                msg=f"服务器异常：{str(exc)}",
                data=None
            ).dict()
        )


