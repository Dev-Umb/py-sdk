"""
HTTP 模块

提供标准化的 HTTP 响应格式和请求处理功能。

主要功能：
- 统一的 API 响应格式（业务状态码）
- 自动 TraceID 注入
- HTTP 客户端封装
- 中间件支持

响应格式：
- HTTP 状态码始终为 200
- 业务状态码在响应 body 中体现
- 自动包含 TraceID 和国际化支持
"""

from .response import (
    APIResponse,
    ResponseBuilder,
    create_response
)

from .code import (
    BusinessCode,
    OK,
    INTERNAL_SERVER_ERROR,
    ROOM_NOT_FOUND,
    UNAUTHORIZED,
    INVALID_PARAMS,
    # 导出常用的业务状态码
)

# 导入 HTTP 客户端
from .client import HttpClient
from .middleware import (
    create_fastapi_middleware,
    create_flask_middleware,
    create_django_middleware
)

__all__ = [
    # 响应相关
    'APIResponse', 
    'ResponseBuilder',
    'create_response',
    
    # 业务状态码
    'BusinessCode',
    'OK',
    'INTERNAL_SERVER_ERROR',
    'ROOM_NOT_FOUND',
    'UNAUTHORIZED',
    'INVALID_PARAMS',
    
    # 客户端
    'HttpClient',
    
    # 中间件
    'create_fastapi_middleware',
    'create_flask_middleware', 
    'create_django_middleware'
] 