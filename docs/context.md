# 上下文管理 (Context)

上下文管理模块提供统一的请求上下文和 TraceID 管理，实现完整的链路追踪功能。

## 🎯 核心功能

- **自动 TraceID 生成**: 每个请求自动生成唯一的 TraceID
- **上下文传递**: 在整个请求链路中自动传递上下文信息
- **异步安全**: 支持异步编程模式，确保上下文隔离
- **HTTP 集成**: 从 HTTP 请求头自动提取和传递 TraceID

## 📦 快速开始

### 基础使用

```python
from context import create_context, set_context, get_current_context

# 1. 创建新的上下文
ctx = create_context()
print(f"TraceID: {ctx.trace_id}")  # 输出: TraceID: abc123def456...

# 2. 设置当前上下文
set_context(ctx)

# 3. 在其他地方获取当前上下文
current_ctx = get_current_context()
print(f"当前 TraceID: {current_ctx.trace_id}")
```

### 自定义 TraceID

```python
from context import create_context

# 使用自定义 TraceID
ctx = create_context(trace_id="my-custom-trace-123")
print(f"TraceID: {ctx.trace_id}")  # 输出: TraceID: my-custom-trace-123
```

### HTTP 请求集成

```python
from context import create_context_from_request
from fastapi import Request

async def handle_request(request: Request):
    # 从 HTTP 请求自动提取 TraceID
    ctx = create_context_from_request(request)
    
    # 如果请求头包含 X-Trace-ID，会自动使用
    # 否则会生成新的 TraceID
    print(f"请求 TraceID: {ctx.trace_id}")
```

## 🔧 API 参考

### Context 类

```python
class Context:
    def __init__(self, trace_id: str = None, **kwargs):
        """
        创建上下文对象
        
        Args:
            trace_id: 自定义 TraceID，为 None 时自动生成
            **kwargs: 其他上下文数据
        """
```

#### 属性

- `trace_id: str` - 链路追踪 ID
- `data: dict` - 额外的上下文数据

#### 方法

```python
def get(self, key: str, default=None):
    """获取上下文数据"""
    
def set(self, key: str, value):
    """设置上下文数据"""
    
def update(self, **kwargs):
    """批量更新上下文数据"""
```

### 核心函数

```python
def create_context(trace_id: str = None, **kwargs) -> Context:
    """
    创建新的上下文对象
    
    Args:
        trace_id: 自定义 TraceID，为 None 时自动生成
        **kwargs: 额外的上下文数据
        
    Returns:
        Context: 上下文对象
    """

def set_context(context: Context):
    """
    设置当前线程/协程的上下文
    
    Args:
        context: 上下文对象
    """

def get_current_context() -> Context:
    """
    获取当前线程/协程的上下文
    
    Returns:
        Context: 当前上下文，如果未设置则返回默认上下文
    """

def create_context_from_request(request) -> Context:
    """
    从 HTTP 请求创建上下文
    
    Args:
        request: HTTP 请求对象（支持 FastAPI、Flask 等）
        
    Returns:
        Context: 从请求提取的上下文
    """
```

## 🌐 Web 框架集成

### FastAPI 集成

```python
from fastapi import FastAPI, Request
from context import create_context_from_request, set_context, get_current_context

app = FastAPI()

@app.middleware("http")
async def context_middleware(request: Request, call_next):
    # 创建并设置上下文
    ctx = create_context_from_request(request)
    set_context(ctx)
    
    # 处理请求
    response = await call_next(request)
    
    # 在响应头中返回 TraceID
    response.headers["X-Trace-ID"] = ctx.trace_id
    return response

@app.get("/api/test")
async def test_endpoint():
    # 在任何地方都可以获取当前上下文
    ctx = get_current_context()
    return {"trace_id": ctx.trace_id, "message": "Hello World"}
```

### Flask 集成

```python
from flask import Flask, request, g
from context import create_context_from_request, set_context, get_current_context

app = Flask(__name__)

@app.before_request
def before_request():
    # 从请求创建上下文
    ctx = create_context_from_request(request)
    set_context(ctx)
    g.context = ctx

@app.after_request
def after_request(response):
    # 在响应头中返回 TraceID
    if hasattr(g, 'context'):
        response.headers['X-Trace-ID'] = g.context.trace_id
    return response

@app.route('/api/test')
def test_endpoint():
    ctx = get_current_context()
    return {"trace_id": ctx.trace_id, "message": "Hello World"}
```

## 🔄 异步编程支持

```python
import asyncio
from context import create_context, set_context, get_current_context

async def process_task(task_id: str):
    # 每个异步任务都有独立的上下文
    ctx = create_context(trace_id=f"task-{task_id}")
    set_context(ctx)
    
    await some_async_operation()
    
    # 在异步操作中仍然可以获取正确的上下文
    current_ctx = get_current_context()
    print(f"任务 {task_id} 的 TraceID: {current_ctx.trace_id}")

async def main():
    # 并发执行多个任务，每个任务的上下文都是隔离的
    tasks = [process_task(str(i)) for i in range(5)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## 📊 链路追踪集成

### 与日志系统集成

```python
from context import create_context, set_context
from logger import get_logger

# 创建上下文
ctx = create_context()
set_context(ctx)

# 获取日志记录器
logger = get_logger("my-service")

# 日志会自动包含 TraceID
logger.info(ctx, "开始处理请求")
logger.info(ctx, "处理完成", extra={"duration": 123})

# 输出:
# 2025-07-03 18:40:00,123 - my-service - INFO - [abc123def456] - 开始处理请求
# 2025-07-03 18:40:00,234 - my-service - INFO - [abc123def456] - 处理完成
```

### 跨服务传递

```python
import requests
from context import get_current_context

def call_downstream_service():
    # 获取当前上下文
    ctx = get_current_context()
    
    # 在 HTTP 请求头中传递 TraceID
    headers = {
        "X-Trace-ID": ctx.trace_id,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "http://downstream-service/api/process",
        json={"data": "some data"},
        headers=headers
    )
    
    return response.json()
```

## 🎛 高级用法

### 上下文数据管理

```python
from context import create_context, set_context, get_current_context

# 创建带额外数据的上下文
ctx = create_context(
    user_id=12345,
    request_id="req-123",
    source="mobile-app"
)
set_context(ctx)

# 在其他地方获取上下文数据
current_ctx = get_current_context()
user_id = current_ctx.get("user_id")
source = current_ctx.get("source", "unknown")

# 动态更新上下文数据
current_ctx.set("step", "validation")
current_ctx.update(
    validated=True,
    validation_time=time.time()
)
```

### 上下文装饰器

```python
from functools import wraps
from context import create_context, set_context, get_current_context

def with_context(trace_id=None, **context_data):
    """为函数创建独立的上下文"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建新的上下文
            ctx = create_context(trace_id=trace_id, **context_data)
            set_context(ctx)
            
            try:
                return func(*args, **kwargs)
            finally:
                # 清理上下文（可选）
                pass
        return wrapper
    return decorator

@with_context(service="user-service", version="1.0")
def process_user_data(user_id):
    ctx = get_current_context()
    print(f"处理用户 {user_id}，TraceID: {ctx.trace_id}")
    print(f"服务: {ctx.get('service')}")
```

## 🔍 调试和监控

### 上下文信息输出

```python
from context import get_current_context

def debug_context():
    ctx = get_current_context()
    print(f"TraceID: {ctx.trace_id}")
    print(f"上下文数据: {ctx.data}")

# 在任何地方调用
debug_context()
```

### 性能监控

```python
import time
from context import get_current_context
from logger import get_logger

def monitor_performance(operation_name: str):
    ctx = get_current_context()
    logger = get_logger("performance")
    
    start_time = time.time()
    
    def finish():
        duration = time.time() - start_time
        logger.info(ctx, f"操作完成: {operation_name}", extra={
            "operation": operation_name,
            "duration_ms": int(duration * 1000)
        })
    
    return finish

# 使用示例
finish = monitor_performance("database_query")
# ... 执行数据库查询
finish()  # 自动记录性能日志
```

## ⚠️ 注意事项

1. **线程安全**: 上下文管理基于 `contextvars`，在多线程环境中每个线程都有独立的上下文
2. **异步安全**: 在异步编程中，每个协程都有独立的上下文
3. **内存管理**: 上下文对象会自动清理，无需手动管理内存
4. **TraceID 格式**: 自动生成的 TraceID 是 32 位十六进制字符串
5. **HTTP 头名称**: 默认使用 `X-Trace-ID` 头传递 TraceID，可配置

## 🔧 配置选项

```python
# 在 Nacos 配置中心配置（可选）
# DataID: context.json
{
    "trace_id_header": "X-Trace-ID",  # HTTP 头名称
    "auto_generate": true,            # 是否自动生成 TraceID
    "trace_id_length": 32             # TraceID 长度
}
``` 