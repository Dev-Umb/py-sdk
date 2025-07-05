# HTTP 客户端 (http_client)

HTTP 客户端模块提供标准化的 HTTP 请求处理和响应格式，支持中间件、错误处理和链路追踪。

## 🎯 核心功能

- **统一响应格式**: 标准化的 HTTP 响应结构
- **自动 TraceID**: 请求和响应自动包含 TraceID
- **中间件支持**: 灵活的请求/响应中间件机制
- **错误处理**: 统一的错误码和错误处理
- **重试机制**: 自动重试和超时控制

## 📦 快速开始

### 基础响应创建

```python
from http_client import create_response, ResponseCode
from context import create_context

# 创建上下文
ctx = create_context()

# 创建成功响应
response = create_response(
    context=ctx,
    code=ResponseCode.SUCCESS,
    data={"message": "Hello World", "user_id": 12345}
)

# 输出:
# {
#     "code": 200,
#     "message": "Success",
#     "data": {"message": "Hello World", "user_id": 12345},
#     "trace_id": "abc123def456",
#     "timestamp": 1672531200
# }
```

### 错误响应创建

```python
from http_client import create_response, ResponseCode

# 创建错误响应
error_response = create_response(
    context=ctx,
    code=ResponseCode.INVALID_PARAM,
    message="用户ID不能为空",
    data={"field": "user_id", "value": None}
)

# 输出:
# {
#     "code": 400,
#     "message": "用户ID不能为空",
#     "data": {"field": "user_id", "value": None},
#     "trace_id": "abc123def456",
#     "timestamp": 1672531200
# }
```

### HTTP 客户端请求

```python
from http_client import HTTPClient
from context import create_context

# 创建 HTTP 客户端
client = HTTPClient()
ctx = create_context()

# 发送 GET 请求
response = client.get(
    url="https://api.example.com/users/123",
    context=ctx,
    headers={"Authorization": "Bearer token"}
)

# 发送 POST 请求
response = client.post(
    url="https://api.example.com/users",
    context=ctx,
    json={"name": "John", "email": "john@example.com"}
)
```

## 🔧 API 参考

### 响应创建函数

```python
def create_response(
    context: Context,
    code: ResponseCode = ResponseCode.SUCCESS,
    message: str = None,
    data: Any = None,
    **kwargs
) -> dict:
    """
    创建标准化响应
    
    Args:
        context: 请求上下文
        code: 响应码
        message: 响应消息（可选，默认使用响应码对应的消息）
        data: 响应数据
        **kwargs: 其他响应字段
        
    Returns:
        dict: 标准化响应字典
    """
```

### ResponseCode 枚举

```python
class ResponseCode:
    # 成功响应 (2xx)
    SUCCESS = 200                    # 成功
    CREATED = 201                   # 创建成功
    ACCEPTED = 202                  # 已接受
    
    # 客户端错误 (4xx)
    BAD_REQUEST = 400              # 请求错误
    UNAUTHORIZED = 401             # 未授权
    FORBIDDEN = 403                # 禁止访问
    NOT_FOUND = 404                # 资源不存在
    METHOD_NOT_ALLOWED = 405       # 方法不允许
    INVALID_PARAM = 400001         # 参数错误
    MISSING_PARAM = 400002         # 缺少参数
    
    # 服务器错误 (5xx)
    INTERNAL_ERROR = 500           # 内部错误
    SERVICE_UNAVAILABLE = 503      # 服务不可用
    TIMEOUT = 504                  # 超时
    DATABASE_ERROR = 500001        # 数据库错误
    EXTERNAL_API_ERROR = 500002    # 外部 API 错误
```

### HTTPClient 类

```python
class HTTPClient:
    def __init__(self, base_url: str = None, timeout: int = 30):
        """
        初始化 HTTP 客户端
        
        Args:
            base_url: 基础 URL
            timeout: 请求超时时间（秒）
        """
    
    def get(self, url: str, context: Context = None, **kwargs) -> dict:
        """发送 GET 请求"""
    
    def post(self, url: str, context: Context = None, **kwargs) -> dict:
        """发送 POST 请求"""
    
    def put(self, url: str, context: Context = None, **kwargs) -> dict:
        """发送 PUT 请求"""
    
    def delete(self, url: str, context: Context = None, **kwargs) -> dict:
        """发送 DELETE 请求"""
    
    def request(self, method: str, url: str, context: Context = None, **kwargs) -> dict:
        """发送自定义请求"""
```

## 📝 使用示例

### 1. Web API 响应

```python
from fastapi import FastAPI
from http_client import create_response, ResponseCode
from context import get_current_context

app = FastAPI()

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    ctx = get_current_context()
    
    try:
        # 查询用户
        user = await get_user_from_db(user_id)
        
        if not user:
            return create_response(
                context=ctx,
                code=ResponseCode.NOT_FOUND,
                message="用户不存在"
            )
        
        return create_response(
            context=ctx,
            code=ResponseCode.SUCCESS,
            data={
                "user_id": user.id,
                "name": user.name,
                "email": user.email
            }
        )
        
    except Exception as e:
        return create_response(
            context=ctx,
            code=ResponseCode.INTERNAL_ERROR,
            message="查询用户失败",
            data={"error": str(e)}
        )

@app.post("/api/users")
async def create_user(user_data: dict):
    ctx = get_current_context()
    
    # 参数验证
    if not user_data.get("name"):
        return create_response(
            context=ctx,
            code=ResponseCode.MISSING_PARAM,
            message="用户名不能为空",
            data={"field": "name"}
        )
    
    try:
        # 创建用户
        user = await create_user_in_db(user_data)
        
        return create_response(
            context=ctx,
            code=ResponseCode.CREATED,
            message="用户创建成功",
            data={"user_id": user.id}
        )
        
    except Exception as e:
        return create_response(
            context=ctx,
            code=ResponseCode.INTERNAL_ERROR,
            message="创建用户失败"
        )
```

### 2. HTTP 客户端调用

```python
from http_client import HTTPClient
from context import create_context
from logger import get_logger

logger = get_logger("api-client")
client = HTTPClient(base_url="https://api.example.com")

async def call_user_service(user_id: int):
    ctx = create_context()
    
    try:
        # 调用用户服务
        response = client.get(
            url=f"/users/{user_id}",
            context=ctx,
            headers={"Authorization": "Bearer token"}
        )
        
        logger.info(ctx, "调用用户服务成功", extra={
            "user_id": user_id,
            "status_code": response.get("status_code")
        })
        
        return response
        
    except Exception as e:
        logger.error(ctx, "调用用户服务失败", extra={
            "user_id": user_id,
            "error": str(e)
        })
        raise

async def create_order(order_data: dict):
    ctx = create_context()
    
    try:
        # 创建订单
        response = client.post(
            url="/orders",
            context=ctx,
            json=order_data,
            timeout=10
        )
        
        if response.get("code") == 200:
            logger.info(ctx, "订单创建成功", extra={
                "order_id": response.get("data", {}).get("order_id")
            })
        else:
            logger.error(ctx, "订单创建失败", extra={
                "error_code": response.get("code"),
                "error_message": response.get("message")
            })
        
        return response
        
    except Exception as e:
        logger.exception(ctx, "订单创建异常", extra={
            "order_data": order_data
        })
        raise
```

### 3. 中间件使用

```python
from http_client import HTTPClient, Middleware
from context import get_current_context
from logger import get_logger

logger = get_logger("http-middleware")

class LoggingMiddleware(Middleware):
    """请求日志中间件"""
    
    def before_request(self, request):
        ctx = get_current_context()
        logger.info(ctx, f"发送请求: {request.method} {request.url}")
        request.start_time = time.time()
        return request
    
    def after_response(self, request, response):
        ctx = get_current_context()
        duration = time.time() - getattr(request, 'start_time', 0)
        
        logger.info(ctx, f"请求完成: {request.method} {request.url}", extra={
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000)
        })
        return response

class AuthMiddleware(Middleware):
    """认证中间件"""
    
    def __init__(self, token: str):
        self.token = token
    
    def before_request(self, request):
        # 自动添加认证头
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

# 使用中间件
client = HTTPClient()
client.add_middleware(LoggingMiddleware())
client.add_middleware(AuthMiddleware("your-token"))

# 发送请求（会自动应用中间件）
response = client.get("https://api.example.com/data")
```

## ⚙️ 配置管理

### Nacos 配置

**DataID**: `http.json`  
**Group**: `DEFAULT_GROUP`

```json
{
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1,
    "max_retry_delay": 60,
    "default_headers": {
        "User-Agent": "py-sdk/1.0.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    "response_format": {
        "success_code": 200,
        "error_code": 500,
        "include_trace_id": true,
        "include_timestamp": true
    },
    "circuit_breaker": {
        "enabled": true,
        "failure_threshold": 5,
        "recovery_timeout": 60
    }
}
```

### 配置项说明

#### 基础配置
- `timeout`: 请求超时时间（秒）
- `retry_count`: 重试次数
- `retry_delay`: 重试延迟（秒）
- `max_retry_delay`: 最大重试延迟（秒）

#### 默认请求头
- `default_headers`: 所有请求的默认头部

#### 响应格式
- `success_code`: 默认成功响应码
- `error_code`: 默认错误响应码
- `include_trace_id`: 是否在响应中包含 TraceID
- `include_timestamp`: 是否在响应中包含时间戳

#### 熔断器配置
- `enabled`: 是否启用熔断器
- `failure_threshold`: 失败阈值
- `recovery_timeout`: 恢复超时时间

## 🔄 重试和熔断

### 自动重试

```python
from http_client import HTTPClient, RetryConfig

# 配置重试策略
retry_config = RetryConfig(
    max_retries=3,
    retry_delay=1,
    backoff_factor=2,
    retry_on_status=[500, 502, 503, 504]
)

client = HTTPClient(retry_config=retry_config)

# 发送请求（失败时会自动重试）
response = client.get("https://api.example.com/data")
```

### 熔断器

```python
from http_client import HTTPClient, CircuitBreakerConfig

# 配置熔断器
circuit_config = CircuitBreakerConfig(
    failure_threshold=5,    # 5次失败后熔断
    recovery_timeout=60,    # 60秒后尝试恢复
    expected_exception=Exception
)

client = HTTPClient(circuit_breaker_config=circuit_config)

try:
    response = client.get("https://api.example.com/data")
except CircuitBreakerOpenException:
    # 熔断器开启，服务不可用
    logger.warning(ctx, "服务熔断，使用降级策略")
    return fallback_response()
```

## 🌐 Web 框架集成

### FastAPI 集成

```python
from fastapi import FastAPI, HTTPException
from http_client import create_response, ResponseCode
from context import get_current_context

app = FastAPI()

# 自定义异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    ctx = get_current_context()
    
    # 根据 HTTP 状态码映射响应码
    code_mapping = {
        400: ResponseCode.BAD_REQUEST,
        401: ResponseCode.UNAUTHORIZED,
        403: ResponseCode.FORBIDDEN,
        404: ResponseCode.NOT_FOUND,
        500: ResponseCode.INTERNAL_ERROR
    }
    
    response_code = code_mapping.get(exc.status_code, ResponseCode.INTERNAL_ERROR)
    
    return create_response(
        context=ctx,
        code=response_code,
        message=exc.detail
    )

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    ctx = get_current_context()
    
    return create_response(
        context=ctx,
        code=ResponseCode.INTERNAL_ERROR,
        message="服务器内部错误",
        data={"error": str(exc)}
    )
```

### Flask 集成

```python
from flask import Flask, jsonify
from http_client import create_response, ResponseCode
from context import get_current_context

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    ctx = get_current_context()
    response = create_response(
        context=ctx,
        code=ResponseCode.NOT_FOUND,
        message="资源不存在"
    )
    return jsonify(response), 404

@app.errorhandler(500)
def internal_error(error):
    ctx = get_current_context()
    response = create_response(
        context=ctx,
        code=ResponseCode.INTERNAL_ERROR,
        message="服务器内部错误"
    )
    return jsonify(response), 500

# 统一响应装饰器
def api_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ctx = get_current_context()
        
        try:
            result = func(*args, **kwargs)
            
            if isinstance(result, dict) and 'code' in result:
                # 已经是标准响应格式
                return jsonify(result)
            else:
                # 包装为标准响应格式
                return jsonify(create_response(
                    context=ctx,
                    code=ResponseCode.SUCCESS,
                    data=result
                ))
                
        except Exception as e:
            return jsonify(create_response(
                context=ctx,
                code=ResponseCode.INTERNAL_ERROR,
                message=str(e)
            )), 500
    
    return wrapper

@app.route('/api/users')
@api_response
def get_users():
    # 返回用户列表
    return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
```

## 🔍 错误处理

### 自定义错误码

```python
from http_client import ResponseCode

# 扩展响应码
class CustomResponseCode(ResponseCode):
    # 业务错误码
    USER_NOT_FOUND = 40001
    USER_ALREADY_EXISTS = 40002
    INSUFFICIENT_BALANCE = 40003
    ORDER_EXPIRED = 40004
    
    # 外部服务错误码
    PAYMENT_SERVICE_ERROR = 50001
    SMS_SERVICE_ERROR = 50002
    EMAIL_SERVICE_ERROR = 50003

# 使用自定义错误码
response = create_response(
    context=ctx,
    code=CustomResponseCode.USER_NOT_FOUND,
    message="用户不存在",
    data={"user_id": user_id}
)
```

### 错误处理装饰器

```python
from functools import wraps
from http_client import create_response, ResponseCode
from context import get_current_context
from logger import get_logger

logger = get_logger("error-handler")

def handle_errors(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        ctx = get_current_context()
        
        try:
            return func(*args, **kwargs)
            
        except ValueError as e:
            logger.warning(ctx, f"参数错误: {str(e)}")
            return create_response(
                context=ctx,
                code=ResponseCode.INVALID_PARAM,
                message=str(e)
            )
            
        except PermissionError as e:
            logger.warning(ctx, f"权限错误: {str(e)}")
            return create_response(
                context=ctx,
                code=ResponseCode.FORBIDDEN,
                message="权限不足"
            )
            
        except Exception as e:
            logger.exception(ctx, f"未知错误: {str(e)}")
            return create_response(
                context=ctx,
                code=ResponseCode.INTERNAL_ERROR,
                message="服务器内部错误"
            )
    
    return wrapper

@handle_errors
def process_user_data(user_id: int):
    if user_id <= 0:
        raise ValueError("用户ID必须大于0")
    
    # 业务逻辑
    return {"user_id": user_id, "status": "processed"}
```

## 🎛 高级功能

### 请求拦截器

```python
from http_client import HTTPClient, RequestInterceptor

class SecurityInterceptor(RequestInterceptor):
    """安全拦截器"""
    
    def intercept(self, request):
        # 添加安全头
        request.headers["X-Request-ID"] = str(uuid.uuid4())
        request.headers["X-Timestamp"] = str(int(time.time()))
        
        # 签名验证
        signature = self.generate_signature(request)
        request.headers["X-Signature"] = signature
        
        return request
    
    def generate_signature(self, request):
        # 生成请求签名
        return hashlib.md5(f"{request.url}{request.body}".encode()).hexdigest()

client = HTTPClient()
client.add_interceptor(SecurityInterceptor())
```

### 响应缓存

```python
from http_client import HTTPClient, CacheConfig

# 配置缓存
cache_config = CacheConfig(
    enabled=True,
    ttl=300,  # 5分钟
    max_size=1000
)

client = HTTPClient(cache_config=cache_config)

# 发送请求（会自动缓存响应）
response1 = client.get("https://api.example.com/data")  # 从服务器获取
response2 = client.get("https://api.example.com/data")  # 从缓存获取
```

### 请求监控

```python
from http_client import HTTPClient, MonitoringConfig
from logger import get_logger

logger = get_logger("http-monitor")

class RequestMonitor:
    def on_request_start(self, request):
        request.start_time = time.time()
        logger.info(None, f"请求开始: {request.method} {request.url}")
    
    def on_request_end(self, request, response):
        duration = time.time() - request.start_time
        logger.info(None, f"请求完成: {request.method} {request.url}", extra={
            "duration_ms": int(duration * 1000),
            "status_code": response.status_code
        })
    
    def on_request_error(self, request, error):
        duration = time.time() - request.start_time
        logger.error(None, f"请求失败: {request.method} {request.url}", extra={
            "duration_ms": int(duration * 1000),
            "error": str(error)
        })

client = HTTPClient()
client.set_monitor(RequestMonitor())
```

## ⚠️ 注意事项

1. **TraceID 传递**: 确保在调用 HTTP 客户端时传入正确的上下文
2. **超时设置**: 根据业务需求合理设置请求超时时间
3. **重试策略**: 谨慎配置重试策略，避免对下游服务造成压力
4. **错误处理**: 统一错误响应格式，便于前端处理
5. **安全性**: 避免在响应中暴露敏感信息

## 📊 最佳实践

1. **统一响应格式**: 所有 API 使用相同的响应结构
2. **错误码规范**: 制定清晰的错误码规范和文档
3. **日志记录**: 记录所有 HTTP 请求和响应的关键信息
4. **性能监控**: 监控 API 响应时间和成功率
5. **版本管理**: API 版本化管理，保持向后兼容 