"""
Python 微服务通用 SDK (py_sdk)

一个为 Python 微服务开发设计的通用工具包，提供统一的日志管理、HTTP 客户端、
上下文管理和服务注册发现等功能。

主要特性：
- 🔧 零配置启动: 所有配置通过 Nacos 自动获取，开箱即用
- 📋 统一日志: 自动包含 TraceID 的结构化日志，支持火山引擎 TLS
- 🌐 HTTP 客户端: 标准化的 HTTP 请求和响应处理
- 🔗 上下文管理: 自动 TraceID 传递，支持异步安全
- 🎯 服务发现: 基于 Nacos 的服务注册与发现
- 📊 可观测性: 完整的链路追踪和日志聚合

快速开始：
    >>> from py_sdk.context import create_context
    >>> from py_sdk.logger import get_logger
    >>> 
    >>> # 创建上下文（自动生成 TraceID）
    >>> ctx = create_context()
    >>> 
    >>> # 获取日志记录器并记录日志
    >>> logger = get_logger("my-service")
    >>> logger.info(ctx, "服务启动成功")
"""

__version__ = "1.0.0"
__author__ = "Your Team"
__email__ = "your-email@example.com"

# 导入核心功能
from .context import (
    Context,
    create_context,
    get_current_context,
    set_context,
    get_trace_id,
    create_context_from_request,
    create_context_from_grpc
)

from .logger import (
    get_logger,
    SDKLogger,
    init_logger_manager
)

from .http_client import (
    APIResponse,
    ResponseBuilder,
    create_response,
    BusinessCode,
    OK,
    INTERNAL_SERVER_ERROR,
    ROOM_NOT_FOUND,
    UNAUTHORIZED,
    INVALID_PARAMS,
    HttpClient,
    create_fastapi_middleware,
    create_flask_middleware,
    create_django_middleware
)

from .nacos_sdk import (
    registerNacos,
    unregisterNacos,
    init_nacos_client,
    init_service_manager,
    register_service,
    unregister_service,
    register_services_from_config,
    cleanup,
    get_config
)

# 导出所有公共 API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    
    # 上下文管理
    "Context",
    "create_context",
    "get_current_context", 
    "set_context",
    "get_trace_id",
    "create_context_from_request",
    "create_context_from_grpc",
    
    # 日志管理
    "get_logger",
    "SDKLogger", 
    "init_logger_manager",
    
    # HTTP 客户端
    "APIResponse",
    "ResponseBuilder",
    "create_response",
    "BusinessCode",
    "OK",
    "INTERNAL_SERVER_ERROR",
    "ROOM_NOT_FOUND", 
    "UNAUTHORIZED",
    "INVALID_PARAMS",
    "HttpClient",
    "create_fastapi_middleware",
    "create_flask_middleware",
    "create_django_middleware",
    
    # Nacos SDK 服务发现
    "registerNacos",
    "unregisterNacos",
    "init_nacos_client",
    "init_service_manager",
    "register_service",
    "unregister_service", 
    "register_services_from_config",
    "cleanup",
    "get_config"
] 