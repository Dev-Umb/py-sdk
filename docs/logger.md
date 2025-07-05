# 日志管理 (Logger)

日志管理模块提供统一的日志记录功能，自动包含 TraceID，支持多种输出方式和火山引擎 TLS 集成。

## 🎯 核心功能

- **自动 TraceID**: 所有日志自动包含当前上下文的 TraceID
- **多种输出**: 支持控制台、文件、火山引擎 TLS 输出
- **结构化日志**: 支持结构化字段，便于日志分析
- **异常处理**: 完整的异常堆栈记录
- **配置热更新**: 支持 Nacos 配置热更新

## 📦 快速开始

### 基础使用

```python
from context import create_context
from logger import get_logger

# 创建上下文
ctx = create_context()

# 获取日志记录器
logger = get_logger("my-service")

# 记录日志（自动包含 TraceID）
logger.info(ctx, "服务启动成功")
logger.warning(ctx, "内存使用率较高")
logger.error(ctx, "数据库连接失败")

# 输出示例:
# 2025-07-03 18:40:00,123 - my-service - INFO - [abc123def456] - 服务启动成功
```

### 结构化日志

```python
from logger import get_logger
from context import create_context

logger = get_logger("user-service")
ctx = create_context()

# 带额外字段的结构化日志
logger.info(ctx, "用户登录", extra={
    "user_id": 12345,
    "username": "john_doe",
    "ip_address": "192.168.1.100",
    "login_time": time.time()
})

# 业务操作日志
logger.info(ctx, "订单创建", extra={
    "order_id": "ORD-2023-001",
    "amount": 99.99,
    "currency": "CNY",
    "payment_method": "alipay"
})
```

### 火山引擎 TLS 集成

```python
from logger import init_logger_manager, get_logger
from context import create_context

# 初始化日志管理器（支持火山引擎 TLS）
init_logger_manager(
    config={
        "handlers": {
            "console": {"enabled": True},
            "tls": {"enabled": True}
        }
    },
    topic_id="2a6a07f0-8490-4a72-9a41-e5f25c578751",  # 必需！
    service_name="my-service"
)

# 使用日志（会同时输出到控制台和 TLS）
logger = get_logger("my-service")
ctx = create_context()
logger.info(ctx, "服务启动", extra={"version": "1.0.0"})
```

## 🔧 API 参考

### 初始化函数

```python
def init_logger_manager(config: dict, topic_id: str = None, service_name: str = None):
    """
    初始化全局日志管理器
    
    Args:
        config: 日志配置字典
        topic_id: 火山引擎 TLS TopicID（使用 TLS 时必需）
        service_name: 服务名称（可选，用于日志标识）
    """

def get_logger(name: str) -> SDKLogger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        SDKLogger: SDK 日志记录器实例
    """
```

### SDKLogger 类

```python
class SDKLogger:
    def debug(self, context: Context, message: str, **kwargs):
        """记录 DEBUG 级别日志"""
    
    def info(self, context: Context, message: str, **kwargs):
        """记录 INFO 级别日志"""
    
    def warning(self, context: Context, message: str, **kwargs):
        """记录 WARNING 级别日志"""
    
    def error(self, context: Context, message: str, **kwargs):
        """记录 ERROR 级别日志"""
    
    def critical(self, context: Context, message: str, **kwargs):
        """记录 CRITICAL 级别日志"""
    
    def exception(self, context: Context, message: str, **kwargs):
        """记录异常日志（自动包含异常堆栈）"""
```

## 📝 使用示例

### 1. 基础日志记录

```python
from context import create_context
from logger import get_logger

logger = get_logger(__name__)
ctx = create_context()

# 不同级别的日志
logger.debug(ctx, "调试信息", extra={"debug_data": "some_value"})
logger.info(ctx, "应用启动")
logger.warning(ctx, "内存使用率较高", extra={"memory_usage": "85%"})
logger.error(ctx, "数据库连接失败", extra={"error_code": "DB_CONN_001"})
logger.critical(ctx, "系统崩溃", extra={"exit_code": 1})
```

### 2. 异常处理

```python
from logger import get_logger
from context import create_context

logger = get_logger("order-service")
ctx = create_context()

try:
    # 业务逻辑
    result = process_order(order_id)
except ValidationError as e:
    logger.error(ctx, "订单验证失败", extra={
        "order_id": order_id,
        "error_code": "VALIDATION_FAILED",
        "details": str(e)
    })
except Exception as e:
    # 使用 exception 方法自动记录异常堆栈
    logger.exception(ctx, "订单处理异常", extra={
        "order_id": order_id,
        "error_type": type(e).__name__
    })
```

### 3. 性能监控

```python
import time
from logger import get_logger
from context import create_context

logger = get_logger("performance")
ctx = create_context()

def monitor_api_call(api_name: str):
    start_time = time.time()
    
    try:
        # API 调用
        result = call_external_api(api_name)
        
        # 记录成功日志
        duration = time.time() - start_time
        logger.info(ctx, f"API 调用成功: {api_name}", extra={
            "api_name": api_name,
            "duration_ms": int(duration * 1000),
            "status": "success"
        })
        
        return result
        
    except Exception as e:
        # 记录失败日志
        duration = time.time() - start_time
        logger.error(ctx, f"API 调用失败: {api_name}", extra={
            "api_name": api_name,
            "duration_ms": int(duration * 1000),
            "status": "failed",
            "error": str(e)
        })
        raise
```

## ⚙️ 配置管理

### Nacos 配置

**DataID**: `logger.json`  
**Group**: `DEFAULT_GROUP`

```json
{
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s",
    "handlers": {
        "console": {
            "enabled": true,
            "level": "INFO"
        },
        "file": {
            "enabled": true,
            "level": "DEBUG",
            "filename": "app.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "tls": {
            "enabled": true,
            "level": "INFO"
        }
    }
}
```

### 火山引擎 TLS 配置

**DataID**: `tls.log.config`  
**Group**: `DEFAULT_GROUP`

```json
{
    "VOLCENGINE_ENDPOINT": "https://tls-cn-beijing.volces.com",
    "VOLCENGINE_ACCESS_KEY_ID": "your-access-key-id",
    "VOLCENGINE_ACCESS_KEY_SECRET": "your-access-key-secret",
    "VOLCENGINE_TOKEN": "",
    "VOLCENGINE_REGION": "cn-beijing"
}
```

### 配置项说明

#### 全局配置
- `level`: 全局日志级别 (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `format`: 日志格式字符串

#### 控制台处理器 (console)
- `enabled`: 是否启用控制台输出
- `level`: 控制台日志级别

#### 文件处理器 (file)
- `enabled`: 是否启用文件输出
- `level`: 文件日志级别
- `filename`: 日志文件名
- `max_bytes`: 单个日志文件最大大小（字节）
- `backup_count`: 保留的日志文件数量

#### TLS 处理器 (tls)
- `enabled`: 是否启用火山引擎 TLS 输出
- `level`: TLS 日志级别

## 🔥 火山引擎 TLS 集成

### 依赖安装

```bash
# 安装火山引擎 SDK
pip install volcengine>=1.0.184

# 安装 LZ4 压缩库（必需）
pip install lz4>=4.0.0
```

### 完整配置示例

```python
from logger import init_logger_manager, get_logger
from context import create_context

# 配置日志管理器
config = {
    "level": "INFO",
    "handlers": {
        "console": {
            "enabled": True,
            "level": "INFO"
        },
        "tls": {
            "enabled": True,
            "level": "INFO"
        }
    }
}

# 初始化（TopicID 是必需的）
init_logger_manager(
    config=config,
    topic_id="2a6a07f0-8490-4a72-9a41-e5f25c578751",
    service_name="my-service"
)

# 使用日志
logger = get_logger("my-service")
ctx = create_context()

logger.info(ctx, "服务启动", extra={
    "version": "1.0.0",
    "environment": "production"
})
```

### 测试 TLS 连接

```python
# 运行测试脚本
python examples/test_tls_logging.py

# 成功输出应包含:
# - TLS 客户端初始化成功
# - POST /PutLogs?TopicId=xxx HTTP/1.1" 200
# - 没有 "TLS API 调用失败" 错误
```

## 🌐 Web 框架集成

### FastAPI 集成

```python
from fastapi import FastAPI, Request
from context import create_context_from_request, set_context
from logger import init_logger_manager, get_logger

# 初始化日志
init_logger_manager(
    config={"handlers": {"console": {"enabled": True}}},
    service_name="api-service"
)

app = FastAPI()
logger = get_logger("api")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # 创建上下文
    ctx = create_context_from_request(request)
    set_context(ctx)
    
    # 记录请求开始
    logger.info(ctx, f"请求开始: {request.method} {request.url}")
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # 记录请求完成
    logger.info(ctx, f"请求完成: {request.method} {request.url}", extra={
        "status_code": response.status_code,
        "duration_ms": int(duration * 1000)
    })
    
    return response

@app.get("/api/health")
async def health_check():
    from context import get_current_context
    ctx = get_current_context()
    logger.info(ctx, "健康检查")
    return {"status": "healthy"}
```

### Flask 集成

```python
from flask import Flask, request, g
from context import create_context_from_request, set_context
from logger import init_logger_manager, get_logger
import time

# 初始化日志
init_logger_manager(
    config={"handlers": {"console": {"enabled": True}}},
    service_name="flask-service"
)

app = Flask(__name__)
logger = get_logger("flask-api")

@app.before_request
def before_request():
    # 创建上下文
    ctx = create_context_from_request(request)
    set_context(ctx)
    g.context = ctx
    g.start_time = time.time()
    
    # 记录请求开始
    logger.info(ctx, f"请求开始: {request.method} {request.url}")

@app.after_request
def after_request(response):
    if hasattr(g, 'context') and hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        
        # 记录请求完成
        logger.info(g.context, f"请求完成: {request.method} {request.url}", extra={
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000)
        })
    
    return response

@app.route('/health')
def health_check():
    logger.info(g.context, "健康检查")
    return {"status": "healthy"}
```

## 🔍 问题排查

### 常见问题

#### 1. TLS 日志发送失败

**症状**: 控制台有日志但 TLS 后台没有数据

**排查步骤**:

```bash
# 1. 检查依赖
pip show volcengine
pip show lz4

# 2. 运行测试
python examples/test_tls_logging.py

# 3. 检查配置
python -c "from nacos.api import get_config; import json; print(json.loads(get_config('tls.log.config')))"
```

**常见错误**:
- `UnsupportedLZ4`: 缺少 lz4 依赖，运行 `pip install lz4`
- `TopicNotExist`: TopicID 不存在或无权限
- `SignatureDoesNotMatch`: AK/SK 错误

#### 2. 日志格式问题

```python
# 检查当前日志配置
from logger import get_logger_manager
manager = get_logger_manager()
print(manager.config)
```

#### 3. 上下文丢失

```python
# 确保正确设置上下文
from context import create_context, set_context, get_current_context

ctx = create_context()
set_context(ctx)

# 验证上下文
current = get_current_context()
print(f"TraceID: {current.trace_id}")
```

### 调试模式

```python
# 开启调试模式
config = {
    "level": "DEBUG",
    "handlers": {
        "console": {
            "enabled": True,
            "level": "DEBUG"
        }
    }
}

init_logger_manager(config)
```

## 🎛 高级功能

### 自定义日志格式

```python
config = {
    "format": "%(asctime)s [%(trace_id)s] %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    "handlers": {
        "console": {"enabled": True}
    }
}
```

### 动态日志级别

```python
import logging
from logger import get_logger_manager

# 动态调整日志级别
manager = get_logger_manager()
logging.getLogger().setLevel(logging.DEBUG)
```

### 日志过滤

```python
import logging

class TraceIDFilter(logging.Filter):
    def filter(self, record):
        # 只记录包含特定 TraceID 的日志
        return hasattr(record, 'trace_id') and record.trace_id.startswith('special')

# 添加过滤器
logger = logging.getLogger()
logger.addFilter(TraceIDFilter())
```

## ⚠️ 注意事项

1. **TopicID 必需**: 使用火山引擎 TLS 时，必须在 `init_logger_manager` 中传入 `topic_id`
2. **依赖要求**: 火山引擎 TLS 需要 `volcengine>=1.0.184` 和 `lz4>=4.0.0`
3. **异步安全**: 所有日志操作都是异步安全的
4. **性能影响**: TLS 日志是异步发送，不会阻塞应用程序
5. **错误处理**: TLS 发送失败时会在 stderr 输出错误信息，不影响应用运行

## 📊 最佳实践

1. **结构化日志**: 使用 `extra` 参数添加结构化字段
2. **合理级别**: 生产环境使用 INFO 级别，开发环境使用 DEBUG
3. **异常处理**: 使用 `logger.exception()` 记录异常堆栈
4. **性能监控**: 记录关键操作的耗时和状态
5. **敏感信息**: 避免在日志中记录密码、密钥等敏感信息 