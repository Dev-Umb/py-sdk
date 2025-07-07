# 日志管理 (Logger)

日志管理模块提供统一的日志记录功能，自动包含 TraceID，支持多种输出方式和火山引擎 TLS 集成。

## 📋 核心功能

- **自动 TraceID**: 所有日志自动包含当前上下文的 TraceID
- **多种输出**: 支持控制台、文件、火山引擎 TLS 输出
- **结构化日志**: 支持结构化字段，便于日志分析
- **高性能**: 异步处理，批量发送，不阻塞主线程
- **零配置**: 开箱即用，无需复杂配置

## 🚀 快速开始

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
    "ip_address": "192.168.1.100"
})

# 业务操作日志
logger.info(ctx, "订单创建", extra={
    "order_id": "ORD-2023-001",
    "amount": 99.99,
    "currency": "CNY"
})
```

### 初始化配置

```python
from logger import init_logger_manager

# 简单初始化（仅控制台输出）
init_logger_manager()

# 启用文件输出
init_logger_manager(
    config={
        "handlers": {
            "file": {
                "enabled": True,
                "filename": "app.log"
            }
        }
    }
)

# 启用火山引擎 TLS
init_logger_manager(
    config={
        "handlers": {
            "tls": {"enabled": True}
        }
    },
    topic_id="your-tls-topic-id",
    service_name="my-service"
)
```

## 📖 API 参考

### get_logger(name)

获取日志记录器实例。

**参数:**
- `name` (str): 日志记录器名称，通常使用 `__name__`

**返回:**
- `SDKLogger`: 日志记录器实例

### init_logger_manager(config=None, topic_id=None, service_name=None)

初始化日志管理器。

**参数:**
- `config` (dict, 可选): 日志配置字典
- `topic_id` (str, 可选): 火山引擎 TLS Topic ID
- `service_name` (str, 可选): 服务名称

### SDKLogger 方法

```python
# 基础日志方法
logger.debug(context, message, extra=None)
logger.info(context, message, extra=None)
logger.warning(context, message, extra=None)
logger.error(context, message, extra=None)
logger.critical(context, message, extra=None)

# 异常日志
logger.exception(context, message, extra=None)
```

## 🔧 配置选项

### 基础配置

```python
config = {
    "level": "INFO",  # 日志级别
    "handlers": {
        "console": {
            "enabled": True,   # 启用控制台输出
            "level": "INFO"    # 控制台日志级别
        },
        "file": {
            "enabled": False,      # 启用文件输出
            "filename": "app.log", # 文件名
            "max_bytes": 10485760, # 文件大小限制
            "backup_count": 5      # 备份文件数量
        },
        "tls": {
            "enabled": False  # 启用火山引擎 TLS
        }
    }
}
```

### 火山引擎 TLS 配置

通过环境变量或 Nacos 配置中心配置：

```bash
# 环境变量
export VOLCENGINE_ENDPOINT=https://tls-cn-beijing.volces.com
export VOLCENGINE_ACCESS_KEY_ID=your-ak
export VOLCENGINE_ACCESS_KEY_SECRET=your-sk
export VOLCENGINE_REGION=cn-beijing
```

## 💡 使用建议

1. **统一日志记录器名称**: 使用 `get_logger(__name__)` 获取日志记录器
2. **传递上下文**: 始终将上下文作为第一个参数传递
3. **使用结构化字段**: 通过 `extra` 参数添加结构化信息
4. **适当的日志级别**: 合理使用不同的日志级别
5. **避免敏感信息**: 不要在日志中记录密码、密钥等敏感信息

## 🔧 集成示例

### 与 FastAPI 集成

```python
from fastapi import FastAPI
from context import create_context
from logger import init_logger_manager, get_logger

# 初始化日志
init_logger_manager()

app = FastAPI()
logger = get_logger("api")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    ctx = create_context()
    
    logger.info(ctx, "获取用户信息", extra={
        "user_id": user_id,
        "endpoint": "/users/{user_id}"
    })
    
    # 业务逻辑
    user = {"id": user_id, "name": "张三"}
    
    logger.info(ctx, "用户信息获取成功", extra={
        "user_id": user_id,
        "user_name": user["name"]
    })
    
    return user
```

### 异常处理

```python
from logger import get_logger
from context import create_context

logger = get_logger("service")

def process_data(data):
    ctx = create_context()
    
    try:
        logger.info(ctx, "开始处理数据", extra={"data_size": len(data)})
        
        # 业务逻辑
        result = complex_processing(data)
        
        logger.info(ctx, "数据处理完成", extra={"result_size": len(result)})
        return result
        
    except Exception as e:
        logger.exception(ctx, "数据处理失败", extra={
            "error_type": type(e).__name__,
            "data_size": len(data)
        })
        raise
```

## 🎯 高级特性

### 高性能 TLS 配置

```python
# 高性能 TLS 配置
config = {
    "handlers": {
        "tls": {
            "enabled": True,
            "batch_size": 200,        # 批量大小
            "batch_timeout": 3.0,     # 批量超时(秒)
            "queue_size": 20000,      # 队列大小
            "worker_threads": 4,      # 工作线程数
            "retry_times": 5          # 重试次数
        }
    }
}

init_logger_manager(
    config=config,
    topic_id="your-topic-id",
    service_name="high-performance-service"
)
```

### 自定义格式化

```python
# 自定义日志格式
config = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s",
    "handlers": {
        "console": {"enabled": True}
    }
}

init_logger_manager(config=config)
``` 