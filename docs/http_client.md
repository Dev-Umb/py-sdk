# HTTP 客户端 (http_client)

HTTP 客户端模块提供标准化的 HTTP 请求处理和响应格式，自动包含 TraceID，支持业务状态码系统。

## 📋 核心功能

- **统一响应格式**: HTTP 状态码始终为 200，业务状态码在 body 中体现
- **自动 TraceID**: 响应中自动包含当前上下文的 TraceID
- **业务状态码**: 丰富的预定义业务状态码，支持自定义
- **简化 API**: 一行代码创建标准响应
- **中间件支持**: 提供各种 Web 框架的中间件

## 🚀 快速开始

### 基础使用

```python
from context import create_context
from http_client import create_response, OK

# 创建上下文
ctx = create_context()

# 创建成功响应
response = create_response(
    context=ctx,
    data={"message": "Hello World", "id": 123}
)

print(response.to_json())
# 输出:
# {
#   "code": 0,
#   "message": "成功",
#   "data": {"message": "Hello World", "id": 123},
#   "trace_id": "abc123def456",
#   "i18n": "success"
# }
```

### 错误响应

```python
from context import create_context
from http_client import create_response, ROOM_NOT_FOUND, UNAUTHORIZED

ctx = create_context()

# 房间不存在错误
error_response = create_response(
    context=ctx,
    code=ROOM_NOT_FOUND
)

# 未授权错误
auth_error = create_response(
    context=ctx,
    code=UNAUTHORIZED
)
```

### 自定义业务状态码

```python
from http_client import BusinessCode, create_response
from context import create_context

# 定义自定义业务状态码
CUSTOM_ERROR = BusinessCode(
    code=10001,
    message="自定义错误",
    i18n="custom_error"
)

ctx = create_context()
response = create_response(
    context=ctx,
    code=CUSTOM_ERROR,
    data={"detail": "具体错误信息"}
)
```

## 📖 API 参考

### create_response(context, code=None, data=None)

创建标准 API 响应。

**参数:**
- `context` (Context, 必需): 上下文对象
- `code` (BusinessCode, 可选): 业务状态码，默认为 OK
- `data` (Any, 可选): 响应数据

**返回:**
- `APIResponse`: API 响应对象

### BusinessCode(code, message, i18n)

业务状态码类。

**参数:**
- `code` (int): 状态码值
- `message` (str): 状态消息
- `i18n` (str): 国际化键值

### APIResponse

标准 API 响应对象。

**属性:**
- `code`: 业务状态码
- `message`: 响应消息
- `data`: 响应数据
- `trace_id`: 链路追踪 ID
- `i18n`: 国际化键值

**方法:**
- `to_dict()`: 转换为字典
- `to_json()`: 转换为 JSON 字符串
- `is_success()`: 是否成功响应
- `is_error()`: 是否错误响应

## 🏷️ 预定义业务状态码

### 成功状态码

```python
OK = BusinessCode(0, "成功", "success")
```

### 错误状态码

```python
# 系统错误
INTERNAL_SERVER_ERROR = BusinessCode(500, "内部服务器错误", "internal_server_error")

# 业务错误
ROOM_NOT_FOUND = BusinessCode(10001, "房间不存在", "room_not_found")
UNAUTHORIZED = BusinessCode(10002, "未授权", "unauthorized")
INVALID_PARAMS = BusinessCode(10003, "参数错误", "invalid_params")
```

## 💡 使用示例

### 1. Web API 响应

```python
from fastapi import FastAPI
from context import create_context_from_request
from http_client import create_response, OK, INVALID_PARAMS

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    # 创建上下文
    ctx = create_context_from_request(request)
    
    # 参数验证
    if user_id <= 0:
        return create_response(
            context=ctx,
            code=INVALID_PARAMS
        ).to_dict()
    
    # 查询用户
    user = get_user_by_id(user_id)
    
    # 返回响应
    return create_response(
        context=ctx,
        code=OK,
        data=user
    ).to_dict()
```

### 2. 微服务调用

```python
from context import create_context
from http_client import create_response, OK
from logger import get_logger

logger = get_logger("user-service")

def process_user_request(user_id):
    """处理用户请求"""
    ctx = create_context()
    
    try:
        logger.info(ctx, "开始处理用户请求", extra={"user_id": user_id})
        
        # 业务逻辑处理
        user_data = query_user_data(user_id)
        
        logger.info(ctx, "用户请求处理成功", extra={
            "user_id": user_id,
            "user_name": user_data.get("name")
        })
        
        # 创建成功响应
        return create_response(
            context=ctx,
            code=OK,
            data=user_data
        )
        
    except UserNotFoundError:
        logger.warning(ctx, "用户不存在", extra={"user_id": user_id})
        return create_response(
            context=ctx,
            code=ROOM_NOT_FOUND  # 复用现有状态码
        )
        
    except Exception as e:
        logger.error(ctx, "处理用户请求失败", extra={
            "user_id": user_id,
            "error": str(e)
        })
        return create_response(
            context=ctx,
            code=INTERNAL_SERVER_ERROR
        )
```

### 3. 自定义状态码

```python
from http_client import BusinessCode, create_response

# 定义业务相关的状态码
USER_NOT_FOUND = BusinessCode(20001, "用户不存在", "user_not_found")
INSUFFICIENT_BALANCE = BusinessCode(20002, "余额不足", "insufficient_balance")
ORDER_EXPIRED = BusinessCode(20003, "订单已过期", "order_expired")

def process_payment(ctx, order_id, amount):
    """处理支付"""
    try:
        # 检查订单
        order = get_order(order_id)
        if not order:
            return create_response(
                context=ctx,
                code=BusinessCode(20004, "订单不存在", "order_not_found")
            )
        
        # 检查余额
        if get_user_balance(order.user_id) < amount:
            return create_response(
                context=ctx,
                code=INSUFFICIENT_BALANCE
            )
        
        # 处理支付
        payment_result = process_payment_logic(order_id, amount)
        
        return create_response(
            context=ctx,
            code=OK,
            data=payment_result
        )
        
    except Exception as e:
        return create_response(
            context=ctx,
            code=INTERNAL_SERVER_ERROR
        )
```

## 🌐 Web 框架集成

### FastAPI 中间件

```python
from fastapi import FastAPI, Request
from context import create_context_from_request
from http_client import create_fastapi_middleware

app = FastAPI()

# 添加上下文中间件
app.add_middleware(create_fastapi_middleware())

@app.get("/api/test")
async def test_api():
    # 自动创建上下文，无需手动处理
    from context import get_current_context
    ctx = get_current_context()
    
    return create_response(
        context=ctx,
        data={"message": "测试成功"}
    ).to_dict()
```

### Flask 集成

```python
from flask import Flask
from http_client import create_flask_middleware

app = Flask(__name__)

# 添加上下文中间件
create_flask_middleware(app)

@app.route('/api/test')
def test_api():
    from context import get_current_context
    ctx = get_current_context()
    
    response = create_response(
        context=ctx,
        data={"message": "测试成功"}
    )
    return response.to_dict()
```

## 🌟 最佳实践

1. **统一响应格式**: 所有 API 都使用 `create_response` 创建响应
2. **业务状态码**: 使用业务状态码而不是 HTTP 状态码表示业务结果
3. **上下文传递**: 始终传递上下文对象，确保 TraceID 的连续性
4. **错误处理**: 合理使用预定义状态码，必要时创建自定义状态码
5. **日志记录**: 结合日志模块记录请求处理过程

## 📊 响应格式规范

### 成功响应

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 123,
    "name": "张三"
  },
  "trace_id": "abc123def456",
  "i18n": "success"
}
```

### 错误响应

```json
{
  "code": 10001,
  "message": "房间不存在",
  "trace_id": "abc123def456",
  "i18n": "room_not_found"
}
```

## 🔗 相关模块

- [context](context.md) - 提供上下文和 TraceID 支持
- [logger](logger.md) - 记录 API 请求处理日志
- [nacos_sdk](nacos_sdk.md) - 微服务间的标准化调用 