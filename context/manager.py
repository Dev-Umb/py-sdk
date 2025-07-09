"""
上下文管理器核心实现

基于 contextvars 实现异步安全的上下文管理，
自动生成 TraceID 并在整个请求周期内传递。
"""

import time
import uuid
import contextvars
import logging
from typing import Optional, Dict, Any, Union

logger = logging.getLogger("py_sdk.context")

# 全局上下文变量
_context_var: contextvars.ContextVar = contextvars.ContextVar('request_context')


class Context:
    """请求上下文类 - 简化版，只包含 TraceID"""
    
    def __init__(self, trace_id: str = None):
        """
        初始化上下文
        
        Args:
            trace_id: 链路追踪ID，如果为空则自动生成
        """
        self.trace_id = trace_id or self._generate_trace_id()
        self.created_at = time.time()
    
    def _generate_trace_id(self) -> str:
        """生成 TraceID"""
        return str(uuid.uuid4()).replace('-', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'trace_id': self.trace_id,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        return f"Context(trace_id={self.trace_id})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.initialized = False
    
    def init(self):
        """初始化上下文管理器"""
        if self.initialized:
            return
        
        self.initialized = True
    
    def create_context(self, trace_id: str = None) -> Context:
        """创建新的上下文"""
        return Context(trace_id=trace_id)
    
    def get_current_context(self) -> Optional[Context]:
        """获取当前上下文"""
        try:
            return _context_var.get()
        except LookupError:
            return None
    
    def set_context(self, context: Context):
        """设置当前上下文"""
        _context_var.set(context)
    
    def get_trace_id(self) -> Optional[str]:
        """获取当前 TraceID"""
        context = self.get_current_context()
        return context.trace_id if context else None
    
    def create_context_from_request(self, request) -> Context:
        """从 HTTP 请求创建上下文"""
        trace_id = None
        
        # 尝试从请求头获取 TraceID
        if hasattr(request, 'headers'):
            trace_id = request.headers.get('X-Trace-Id') or request.headers.get('x-trace-id')
        
        return Context(trace_id=trace_id)
    
    def create_context_from_grpc(self, grpc_context) -> Context:
        """从 gRPC 上下文创建上下文"""
        trace_id = None
        
        # 尝试从 gRPC 元数据获取 TraceID
        try:
            metadata = dict(grpc_context.invocation_metadata())
            trace_id = metadata.get('x-trace-id') or metadata.get('trace-id')
        except Exception:
            pass
        
        return Context(trace_id=trace_id)


# 全局上下文管理器实例
_context_manager: Optional[ContextManager] = None


def init_context_manager():
    """初始化全局上下文管理器"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
        _context_manager.init()


def get_context_manager() -> ContextManager:
    """获取全局上下文管理器"""
    if _context_manager is None:
        init_context_manager()
    return _context_manager


def create_context(trace_id: str = None) -> Context:
    """
    创建新的上下文（自动生成 TraceID）
    
    Args:
        trace_id: 可选的 TraceID，如果不提供则自动生成
        
    Returns:
        新创建的上下文
        
    Example:
        >>> ctx = create_context()
        >>> print(ctx.trace_id)  # 自动生成的 TraceID
        
        >>> ctx = create_context("custom-trace-id")
        >>> print(ctx.trace_id)  # custom-trace-id
    """
    manager = get_context_manager()
    context = manager.create_context(trace_id=trace_id)
    manager.set_context(context)
    return context


def get_current_context() -> Optional[Context]:
    """
    获取当前上下文
    
    Returns:
        当前上下文，如果没有则返回 None
        
    Example:
        >>> ctx = get_current_context()
        >>> if ctx:
        >>>     print(f"TraceID: {ctx.trace_id}")
    """
    manager = get_context_manager()
    return manager.get_current_context()


def set_context(context: Context):
    """
    设置当前上下文
    
    Args:
        context: 要设置的上下文
        
    Example:
        >>> ctx = Context(user_id="123")
        >>> set_context(ctx)
    """
    manager = get_context_manager()
    manager.set_context(context)


def get_trace_id() -> Optional[str]:
    """
    获取当前 TraceID
    
    Returns:
        当前 TraceID，如果没有上下文则返回 None
        
    Example:
        >>> trace_id = get_trace_id()
        >>> print(f"当前 TraceID: {trace_id}")
    """
    manager = get_context_manager()
    return manager.get_trace_id()


def create_context_from_request(request) -> Context:
    """
    从 HTTP 请求创建上下文
    
    Args:
        request: HTTP 请求对象（Flask/Django/FastAPI 等）
        
    Returns:
        从请求创建的上下文
        
    Example:
        >>> # Flask
        >>> from flask import request
        >>> ctx = create_context_from_request(request)
        >>> set_context(ctx)
    """
    manager = get_context_manager()
    context = manager.create_context_from_request(request)
    manager.set_context(context)
    return context


def create_context_from_grpc(grpc_context) -> Context:
    """
    从 gRPC 上下文创建上下文
    
    Args:
        grpc_context: gRPC 服务上下文
        
    Returns:
        从 gRPC 上下文创建的上下文
        
    Example:
        >>> def GetUser(self, request, context):
        >>>     ctx = create_context_from_grpc(context)
        >>>     # 业务逻辑
    """
    manager = get_context_manager()
    context = manager.create_context_from_grpc(grpc_context)
    manager.set_context(context)
    return context 