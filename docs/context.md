# 上下文管理 (Context)

上下文管理模块提供基于 contextvars 的异步安全上下文管理，自动生成和传递 TraceID。

## 📋 核心功能

- **自动生成 TraceID**: 基于 UUID 生成唯一的链路追踪 ID
- **异步安全**: 使用 contextvars 确保在异步环境中的上下文隔离
- **简单易用**: 极简的 API 设计，3 行代码即可使用
- **自动传递**: 在整个请求周期内自动传递上下文信息

## 🚀 快速开始

### 基础使用

```python
from context import create_context, get_trace_id

# 创建上下文（自动生成 TraceID）
ctx = create_context()
print(f"TraceID: {ctx.trace_id}")

# 获取当前 TraceID
trace_id = get_trace_id()
print(f"当前 TraceID: {trace_id}")
```

### 自定义 TraceID

```python
from context import create_context

# 使用自定义 TraceID
ctx = create_context(trace_id="custom-trace-id")
print(f"自定义 TraceID: {ctx.trace_id}")
```

### 从 HTTP 请求创建上下文

```python
from context import create_context_from_request

# 从 HTTP 请求头获取 TraceID
def handle_request(request):
    ctx = create_context_from_request(request)
    # 如果请求头包含 X-Trace-Id，会自动使用
    # 否则自动生成新的 TraceID
    return ctx
```

## 📖 API 参考

### create_context(trace_id=None)

创建新的上下文并设置为当前上下文。

**参数:**
- `trace_id` (str, 可选): 自定义 TraceID，如果不提供则自动生成

**返回:**
- `Context`: 新创建的上下文对象

### get_current_context()

获取当前上下文。

**返回:**
- `Context`: 当前上下文对象，如果没有则返回 None

### get_trace_id()

获取当前 TraceID。

**返回:**
- `str`: 当前 TraceID，如果没有上下文则返回 None

### create_context_from_request(request)

从 HTTP 请求创建上下文，自动从请求头提取 TraceID。

**参数:**
- `request`: HTTP 请求对象

**返回:**
- `Context`: 新创建的上下文对象

### create_context_from_grpc(grpc_context)

从 gRPC 上下文创建上下文。

**参数:**
- `grpc_context`: gRPC 上下文对象

**返回:**
- `Context`: 新创建的上下文对象

## 🔧 Context 对象

### 属性
- `trace_id`: 链路追踪 ID
- `created_at`: 创建时间戳

### 方法
- `to_dict()`: 转换为字典格式
- `__str__()`: 字符串表示

## 💡 使用建议

### 1. 在应用入口创建上下文

```python
# 在请求处理开始时创建上下文
def handle_request(request):
    ctx = create_context_from_request(request)
    # 后续所有操作都会自动使用这个上下文
    process_business_logic()
```

### 2. 异步环境中的使用

```python
import asyncio
from context import create_context, get_trace_id

async def async_function():
    ctx = create_context()
    print(f"异步函数中的 TraceID: {get_trace_id()}")
    
    # 在异步任务中，上下文会自动传递
    await another_async_function()

async def another_async_function():
    # 可以直接获取上层函数的 TraceID
    trace_id = get_trace_id()
    print(f"另一个异步函数中的 TraceID: {trace_id}")
```

### 3. Web 框架集成

```python
# FastAPI 示例
from fastapi import FastAPI, Request
from context import create_context_from_request

app = FastAPI()

@app.middleware("http")
async def context_middleware(request: Request, call_next):
    ctx = create_context_from_request(request)
    response = await call_next(request)
    return response

# Flask 示例
from flask import Flask, request
from context import create_context_from_request

app = Flask(__name__)

@app.before_request
def before_request():
    ctx = create_context_from_request(request)
```

## 🌟 最佳实践

1. **统一入口**: 在应用的统一入口（如中间件）创建上下文
2. **自动传递**: 利用 contextvars 的特性，上下文会自动在调用链中传递
3. **TraceID 传递**: 在微服务调用时，将 TraceID 添加到请求头中
4. **异步安全**: 在异步环境中使用时，上下文会自动隔离，无需手动管理

## 🔗 相关模块

- [logger](logger.md) - 日志模块会自动使用上下文中的 TraceID
- [http_client](http_client.md) - HTTP 响应中会自动包含 TraceID 