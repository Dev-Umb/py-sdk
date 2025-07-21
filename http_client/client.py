"""
HTTP 客户端

提供统一的 HTTP 客户端，自动注入 TraceID，
支持重试、超时和连接池管理。
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter

import py_sdk
from ..context.manager import get_current_context
from .response import APIResponse
from .code import INTERNAL_SERVER_ERROR
from ..nacos_sdk.api import get_config

# 安全导入 urllib3
try:
    from urllib3.util.retry import Retry
except ImportError:
    # 如果 urllib3 导入失败，使用 requests 的重试机制
    from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger("py_sdk.http")

# 默认配置
DEFAULT_CONFIG = {
    "timeout": 30,
    "retry_count": 3,
    "retry_backoff_factor": 0.3,
    "retry_status_forcelist": [500, 502, 503, 504],
    "pool_connections": 10,
    "pool_maxsize": 10,
    "default_headers": {
        "User-Agent": "py_sdk/1.0.0",
        "Content-Type": "application/json"
    }
}


class HttpClient:
    """HTTP 客户端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 HTTP 客户端
        
        Args:
            config: 配置字典，如果为空则从 Nacos 获取
        """
        self.config = self._load_config(config)
        self.session = self._create_session()
        self.context = py_sdk.create_context()
        logger.info(self.context,"HTTP 客户端初始化完成")
    
    def _load_config(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """加载配置"""
        if config:
            result = DEFAULT_CONFIG.copy()
            result.update(config)
            return result
        
        # 尝试从 Nacos 获取配置
        try:
            nacos_config = get_config("http.json")
            if nacos_config:
                nacos_data = json.loads(nacos_config)
                result = DEFAULT_CONFIG.copy()
                result.update(nacos_data)
                logger.info(self.context,"从 Nacos 加载 HTTP 配置成功")
                return result
        except Exception as e:
            logger.warning(self.context, f"从 Nacos 加载 HTTP 配置失败: {str(e)}")
        
        logger.info(self.context,"使用默认 HTTP 配置")
        return DEFAULT_CONFIG.copy()
    
    def _create_session(self) -> requests.Session:
        """创建会话对象"""
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=self.config.get("retry_count", 3),
            backoff_factor=self.config.get("retry_backoff_factor", 0.3),
            status_forcelist=self.config.get("retry_status_forcelist", [500, 502, 503, 504])
        )
        
        # 设置适配器
        adapter = HTTPAdapter(
            pool_connections=self.config.get("pool_connections", 10),
            pool_maxsize=self.config.get("pool_maxsize", 10),
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认头部
        default_headers = self.config.get("default_headers", {})
        session.headers.update(default_headers)
        
        return session
    
    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """准备请求头"""
        final_headers = {}
        
        # 添加 TraceID
        context = get_current_context()
        if context:
            final_headers["X-Trace-Id"] = context.trace_id
        
        # 合并用户提供的头部
        if headers:
            final_headers.update(headers)
        
        return final_headers
    
    def _make_request(self, method: str, url: str, **kwargs) -> APIResponse:
        """执行 HTTP 请求"""
        start_time = time.time()
        
        # 准备请求头
        headers = self._prepare_headers(kwargs.pop("headers", None))
        
        # 设置超时
        timeout = kwargs.pop("timeout", self.config.get("timeout", 30))
        
        try:
            logger.debug(f"发起 {method} 请求: {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            
            elapsed_time = time.time() - start_time
            logger.debug(f"{method} {url} - {response.status_code} - {elapsed_time:.3f}s")
            
            return self._parse_response(response)
            
        except requests.exceptions.Timeout:
            logger.error(self.context,f"请求超时: {method} {url}")
            return APIResponse(
                business_code=INTERNAL_SERVER_ERROR,
                data={"error": "请求超时"}
            )
        except requests.exceptions.ConnectionError:
            logger.error(self.context,f"连接错误: {method} {url}")
            return APIResponse(
                business_code=INTERNAL_SERVER_ERROR,
                data={"error": "连接错误"}
            )
        except Exception as e:
            logger.error(self.context,f"请求异常: {method} {url} - {str(e)}")
            return APIResponse(
                business_code=INTERNAL_SERVER_ERROR,
                data={"error": f"请求异常: {str(e)}"}
            )
    
    def _parse_response(self, response: requests.Response) -> APIResponse:
        """解析响应"""
        from .code import OK
        
        try:
            # 尝试解析 JSON
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
            else:
                data = response.text
            
            # 如果响应已经是标准格式，直接使用
            if isinstance(data, dict) and "code" in data and "message" in data:
                # 根据业务状态码判断成功或失败
                business_code = OK if data.get("code", 0) == 0 else INTERNAL_SERVER_ERROR
                return APIResponse(
                    business_code=business_code,
                    data=data.get("data"),
                    trace_id=data.get("trace_id")
                )
            
            # 否则包装为标准格式
            business_code = OK if response.ok else INTERNAL_SERVER_ERROR
            
            return APIResponse(
                business_code=business_code,
                data=data
            )
            
        except json.JSONDecodeError:
            return APIResponse(
                business_code=INTERNAL_SERVER_ERROR,
                data={"error": "响应格式错误", "raw": response.text}
            )
    
    def get(self, url: str, params: Dict[str, Any] = None, **kwargs) -> APIResponse:
        """GET 请求"""
        return self._make_request("GET", url, params=params, **kwargs)
    
    def post(self, url: str, data: Any = None, json_data: Any = None, **kwargs) -> APIResponse:
        """POST 请求"""
        if json_data is not None:
            kwargs["json"] = json_data
        elif data is not None:
            kwargs["data"] = data
        
        return self._make_request("POST", url, **kwargs)
    
    def put(self, url: str, data: Any = None, json_data: Any = None, **kwargs) -> APIResponse:
        """PUT 请求"""
        if json_data is not None:
            kwargs["json"] = json_data
        elif data is not None:
            kwargs["data"] = data
        
        return self._make_request("PUT", url, **kwargs)
    
    def patch(self, url: str, data: Any = None, json_data: Any = None, **kwargs) -> APIResponse:
        """PATCH 请求"""
        if json_data is not None:
            kwargs["json"] = json_data
        elif data is not None:
            kwargs["data"] = data
        
        return self._make_request("PATCH", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> APIResponse:
        """DELETE 请求"""
        return self._make_request("DELETE", url, **kwargs)
    
    def head(self, url: str, **kwargs) -> APIResponse:
        """HEAD 请求"""
        return self._make_request("HEAD", url, **kwargs)
    
    def options(self, url: str, **kwargs) -> APIResponse:
        """OPTIONS 请求"""
        return self._make_request("OPTIONS", url, **kwargs)


# 全局 HTTP 客户端实例
_http_client: Optional[HttpClient] = None


def get_http_client() -> HttpClient:
    """获取全局 HTTP 客户端实例"""
    global _http_client
    if _http_client is None:
        _http_client = HttpClient()
    return _http_client


def init_http_client(config: Dict[str, Any] = None):
    """初始化全局 HTTP 客户端"""
    global _http_client
    _http_client = HttpClient(config)


# 便捷方法
def get(url: str, **kwargs) -> APIResponse:
    """GET 请求便捷方法"""
    return get_http_client().get(url, **kwargs)


def post(url: str, **kwargs) -> APIResponse:
    """POST 请求便捷方法"""
    return get_http_client().post(url, **kwargs)


def put(url: str, **kwargs) -> APIResponse:
    """PUT 请求便捷方法"""
    return get_http_client().put(url, **kwargs)


def patch(url: str, **kwargs) -> APIResponse:
    """PATCH 请求便捷方法"""
    return get_http_client().patch(url, **kwargs)


def delete(url: str, **kwargs) -> APIResponse:
    """DELETE 请求便捷方法"""
    return get_http_client().delete(url, **kwargs) 