"""
HTTP 响应格式标准化

提供统一的 API 响应格式，自动包含 TraceID。
HTTP 响应始终为 200，业务状态码在 body 中体现。
"""

import json
import time
from typing import Any, Dict, Optional, Union
from ..context.manager import get_current_context, Context
from .code import BusinessCode, OK


class APIResponse:
    """标准 API 响应类"""
    
    def __init__(self, business_code: BusinessCode, data: Any = None, 
                 trace_id: str = None, i18n: str = "", timestamp: int = None):
        """
        初始化 API 响应
        
        Args:
            business_code: 业务状态码
            data: 响应数据
            trace_id: 链路追踪ID
            i18n: 国际化键值
            timestamp: 时间戳
        """
        self.business_code = business_code
        self.data = data
        self.trace_id = trace_id or self._get_trace_id()
        self.i18n = i18n or business_code.i18n
        self.timestamp = timestamp or int(time.time())
    
    def _get_trace_id(self) -> str:
        """获取当前上下文的 TraceID"""
        context = get_current_context()
        return context.trace_id if context else "unknown"
    
    @property
    def code(self) -> int:
        """获取业务状态码"""
        return self.business_code.code
    
    @property
    def message(self) -> str:
        """获取响应消息"""
        return self.business_code.message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "code": self.code,
            "message": self.message,
            "i18n": self.i18n,
            "trace_id": self.trace_id
        }
        
        # 只有当 data 不为 None 时才添加
        if self.data is not None:
            result["data"] = self.data
            
        return result
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def is_success(self) -> bool:
        """判断是否成功响应"""
        return self.code == 0
    
    def is_error(self) -> bool:
        """判断是否错误响应"""
        return self.code != 0
    
    def __str__(self) -> str:
        return f"APIResponse(code={self.code}, message='{self.message}', trace_id='{self.trace_id}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class ResponseBuilder:
    """响应构建器"""
    
    def __init__(self, context: Context, business_code: BusinessCode = None):
        """
        初始化响应构建器
        
        Args:
            context: 上下文对象（必需）
            business_code: 业务状态码（默认为成功）
        """
        if context is None:
            raise ValueError("context 参数是必需的，不能为 None")
        
        self._context = context
        self._business_code = business_code or OK
        self._data = None
        self._i18n = ""
        self._timestamp = None
    
    def code(self, business_code: BusinessCode) -> 'ResponseBuilder':
        """设置业务状态码"""
        self._business_code = business_code
        return self
    
    def success(self, business_code: BusinessCode = None) -> 'ResponseBuilder':
        """设置成功状态"""
        self._business_code = business_code or OK
        return self
    
    def error(self, business_code: BusinessCode) -> 'ResponseBuilder':
        """设置错误状态"""
        self._business_code = business_code
        return self
    
    def i18n(self, i18n: str) -> 'ResponseBuilder':
        """设置国际化键值"""
        self._i18n = i18n
        return self
    
    def data(self, data: Any) -> 'ResponseBuilder':
        """设置数据"""
        self._data = data
        return self
    

    
    def timestamp(self, timestamp: int) -> 'ResponseBuilder':
        """设置时间戳"""
        self._timestamp = timestamp
        return self
    
    def build(self) -> APIResponse:
        """构建响应对象"""
        return APIResponse(
            business_code=self._business_code,
            data=self._data,
            trace_id=self._context.trace_id,
            i18n=self._i18n,
            timestamp=self._timestamp
        )


def create_response(context: Context,
                   code: BusinessCode = None,
                   data: Any = None) -> APIResponse:
    """
    创建标准 API 响应（必须传入上下文）
    
    Args:
        context: 上下文对象（必需）
        code: 业务状态码（可选，默认为 OK）
        data: 响应数据（可选）
        
    Returns:
        API 响应对象
        
    Example:
        >>> from http_client.code import ROOM_NOT_FOUND
        >>> ctx = create_context()
        >>> 
        >>> # 成功响应（默认使用 OK）
        >>> response = create_response(
        ...     context=ctx,
        ...     data={"id": 1, "name": "test"}
        ... )
        >>> 
        >>> # 错误响应
        >>> error_response = create_response(
        ...     context=ctx,
        ...     code=ROOM_NOT_FOUND
        ... )
        >>> print(error_response.to_json())
    """
    if context is None:
        raise ValueError("context 参数是必需的，不能为 None")
    
    # 如果没有提供业务状态码，默认为成功
    if code is None:
        code = OK
    
    return APIResponse(
        business_code=code,
        data=data,
        trace_id=context.trace_id,
        i18n=code.i18n  # 使用 code 自带的 i18n
    )


# 注意：现在只使用统一的 create_response 函数
# 所有响应都通过 create_response(context, code, data) 创建
# 
# 使用示例：
# 1. 成功响应（默认 OK）：
#    response = create_response(ctx, data={"id": 1, "name": "test"})
#
# 2. 成功响应（指定状态码）：
#    response = create_response(ctx, code=OK, data={"result": "success"})
#
# 3. 错误响应：
#    response = create_response(ctx, code=ROOM_NOT_FOUND)
#
# 4. 分页响应：
#    data = {
#        "items": items,
#        "pagination": {
#            "total": total,
#            "page": page,
#            "page_size": page_size,
#            "total_pages": (total + page_size - 1) // page_size
#        }
#    }
#    response = create_response(ctx, data=data) 