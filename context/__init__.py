"""
上下文管理模块 - 简化版

提供基于 contextvars 的异步安全上下文管理，
自动生成 TraceID 并在整个请求周期内传递。

主要功能：
- 自动生成 UUID 格式的 TraceID
- 异步安全的上下文传递
- 极简的 API 设计

使用示例：
    >>> from context import create_context, get_trace_id
    >>> 
    >>> # 创建上下文（自动生成 TraceID）
    >>> ctx = create_context()
    >>> print(ctx.trace_id)
    >>> 
    >>> # 获取当前 TraceID
    >>> trace_id = get_trace_id()
"""

from .manager import (
    Context,
    create_context,
    get_current_context,
    set_context,
    get_trace_id,
    create_context_from_request,
    create_context_from_grpc,
    context_scope
)

__all__ = [
    'Context',
    'create_context',
    'get_current_context',
    'set_context',
    'get_trace_id',
    'create_context_from_request',
    'create_context_from_grpc',
    'context_scope'
] 