"""
HTTP 中间件

提供各种 Web 框架的中间件集成，
自动处理上下文创建和 TraceID 传递。
"""

import logging
from typing import Callable, Any
from ..context.manager import create_context_from_request, set_context, get_current_context
from ..logger.manager import get_logger

logger = get_logger("py_sdk.http.middleware")


def create_fastapi_middleware():
    """
    创建 FastAPI 中间件
    
    Returns:
        FastAPI 中间件函数
        
    Example:
        >>> from fastapi import FastAPI
        >>> from http_client.middleware import create_fastapi_middleware
        >>> 
        >>> app = FastAPI()
        >>> app.middleware("http")(create_fastapi_middleware())
    """
    
    async def middleware(request, call_next):
        """FastAPI 中间件实现"""
        # 从请求创建上下文
        ctx = create_context_from_request(request)
        set_context(ctx)
        
        # 记录请求开始日志
        logger.info(ctx, f"收到请求: {request.method} {request.url}")
        
        try:
            # 执行请求处理
            response = await call_next(request)
            
            # 添加 TraceID 到响应头
            response.headers["X-Trace-Id"] = ctx.trace_id
            
            # 记录请求完成日志
            logger.info(ctx, f"请求完成: {request.method} {request.url} - {response.status_code}")
            
            return response
            
        except Exception as e:
            # 记录异常日志
            logger.exception(ctx, f"请求处理异常: {request.method} {request.url}")
            raise
    
    return middleware


def create_flask_middleware(app):
    """
    创建 Flask 中间件
    
    Args:
        app: Flask 应用实例
        
    Example:
        >>> from flask import Flask
        >>> from http_client.middleware import create_flask_middleware
        >>> 
        >>> app = Flask(__name__)
        >>> create_flask_middleware(app)
    """
    
    @app.before_request
    def before_request():
        """请求前处理"""
        from flask import request
        
        # 从请求创建上下文
        ctx = create_context_from_request(request)
        set_context(ctx)
        
        # 记录请求开始日志
        logger.info(ctx, f"收到请求: {request.method} {request.url}")
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        from flask import request
        
        ctx = get_current_context()
        if ctx:
            # 添加 TraceID 到响应头
            response.headers["X-Trace-Id"] = ctx.trace_id
            
            # 记录请求完成日志
            logger.info(ctx, f"请求完成: {request.method} {request.url} - {response.status_code}")
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """异常处理"""
        from flask import request
        
        ctx = get_current_context()
        if ctx:
            logger.exception(ctx, f"请求处理异常: {request.method} {request.url}")
        
        # 重新抛出异常，让 Flask 的默认错误处理器处理
        raise


def create_django_middleware():
    """
    创建 Django 中间件类
    
    Returns:
        Django 中间件类
        
    Example:
        >>> # 在 Django settings.py 中添加
        >>> MIDDLEWARE = [
        ...     'your_app.middleware.TraceIDMiddleware',
        ...     # 其他中间件
        ... ]
        >>> 
        >>> # 在 your_app/middleware.py 中
        >>> from http_client.middleware import create_django_middleware
        >>> TraceIDMiddleware = create_django_middleware()
    """
    
    class TraceIDMiddleware:
        """Django TraceID 中间件"""
        
        def __init__(self, get_response):
            self.get_response = get_response
        
        def __call__(self, request):
            # 从请求创建上下文
            ctx = create_context_from_request(request)
            set_context(ctx)
            
            # 记录请求开始日志
            logger.info(ctx, f"收到请求: {request.method} {request.get_full_path()}")
            
            try:
                # 执行请求处理
                response = self.get_response(request)
                
                # 添加 TraceID 到响应头
                response["X-Trace-Id"] = ctx.trace_id
                
                # 记录请求完成日志
                logger.info(ctx, f"请求完成: {request.method} {request.get_full_path()} - {response.status_code}")
                
                return response
                
            except Exception as e:
                # 记录异常日志
                logger.exception(ctx, f"请求处理异常: {request.method} {request.get_full_path()}")
                raise
    
    return TraceIDMiddleware


def create_tornado_middleware():
    """
    创建 Tornado 中间件基类
    
    Returns:
        Tornado RequestHandler 基类
        
    Example:
        >>> from tornado.web import Application
        >>> from http_client.middleware import create_tornado_middleware
        >>> 
        >>> class MyHandler(create_tornado_middleware()):
        ...     def get(self):
        ...         self.write({"message": "Hello World"})
        >>> 
        >>> app = Application([
        ...     (r"/", MyHandler),
        ... ])
    """
    
    import tornado.web
    
    class BaseHandler(tornado.web.RequestHandler):
        """Tornado 基础处理器"""
        
        def prepare(self):
            """请求准备阶段"""
            # 从请求创建上下文
            ctx = create_context_from_request(self.request)
            set_context(ctx)
            
            # 记录请求开始日志
            logger.info(ctx, f"收到请求: {self.request.method} {self.request.uri}")
        
        def on_finish(self):
            """请求完成阶段"""
            ctx = get_current_context()
            if ctx:
                # 添加 TraceID 到响应头
                self.set_header("X-Trace-Id", ctx.trace_id)
                
                # 记录请求完成日志
                logger.info(ctx, f"请求完成: {self.request.method} {self.request.uri} - {self.get_status()}")
        
        def write_error(self, status_code, **kwargs):
            """错误处理"""
            ctx = get_current_context()
            if ctx:
                logger.exception(ctx, f"请求处理异常: {self.request.method} {self.request.uri}")
            
            super().write_error(status_code, **kwargs)
    
    return BaseHandler


class WSGIMiddleware:
    """WSGI 中间件"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        """WSGI 调用"""
        # 创建简单的请求对象
        class SimpleRequest:
            def __init__(self, environ):
                self.method = environ.get('REQUEST_METHOD', 'GET')
                self.url = environ.get('REQUEST_URI', '/')
                self.headers = self._parse_headers(environ)
            
            def _parse_headers(self, environ):
                headers = {}
                for key, value in environ.items():
                    if key.startswith('HTTP_'):
                        header_name = key[5:].replace('_', '-').lower()
                        headers[header_name] = value
                return headers
        
        # 从请求创建上下文
        request = SimpleRequest(environ)
        ctx = create_context_from_request(request)
        set_context(ctx)
        
        # 记录请求开始日志
        logger.info(ctx, f"收到请求: {request.method} {request.url}")
        
        def new_start_response(status, response_headers, exc_info=None):
            # 添加 TraceID 到响应头
            response_headers.append(('X-Trace-Id', ctx.trace_id))
            
            # 记录请求完成日志
            status_code = int(status.split()[0])
            logger.info(ctx, f"请求完成: {request.method} {request.url} - {status_code}")
            
            return start_response(status, response_headers, exc_info)
        
        try:
            return self.app(environ, new_start_response)
        except Exception as e:
            # 记录异常日志
            logger.exception(ctx, f"请求处理异常: {request.method} {request.url}")
            raise 