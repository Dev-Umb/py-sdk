# 常见问题解答 (FAQ)

本文档收集了使用 py-sdk 过程中的常见问题和解决方案。

## 🚀 快速开始问题

### Q1: 如何快速验证 SDK 是否正常工作？

**A**: 运行以下简单测试：

```python
from context import create_context
from logger import get_logger

# 创建上下文
ctx = create_context()
print(f"TraceID: {ctx.trace_id}")

# 测试日志
logger = get_logger("test")
logger.info(ctx, "SDK 工作正常")
```

如果能看到包含 TraceID 的日志输出，说明 SDK 基本功能正常。

### Q2: 为什么导入模块时报错？

**A**: 检查以下几点：

1. **确认安装了依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **检查 Python 路径**：
   ```python
   import sys
   print(sys.path)
   ```

3. **确认模块在正确位置**：
   ```bash
   ls -la context/ logger/ http_client/ nacos/
   ```

## 🔧 配置相关问题

### Q3: Nacos 连接失败怎么办？

**A**: 按以下步骤排查：

1. **检查网络连通性**：
   ```bash
   telnet nacos-server 8848
   # 或者
   curl http://nacos-server:8848/nacos
   ```

2. **验证环境变量**：
   ```bash
   echo $NACOS_ADDRESS
   echo $NACOS_NAMESPACE
   echo $NACOS_USERNAME
   ```

3. **测试连接**：
   ```python
   from nacos import get_config
   
   try:
       config = get_config("test", "DEFAULT_GROUP")
       print("连接成功")
   except Exception as e:
       print(f"连接失败: {e}")
   ```

### Q4: 配置获取为空或失败？

**A**: 检查配置是否存在：

1. **在 Nacos 控制台确认配置存在**
2. **检查 DataID 和 Group 是否正确**
3. **验证命名空间配置**：
   ```python
   # 检查当前命名空间
   import os
   print(f"Namespace: {os.environ.get('NACOS_NAMESPACE', 'public')}")
   ```

### Q5: 如何在不同环境使用不同配置？

**A**: 使用环境变量或命名空间隔离：

```python
import os

# 方法1：使用不同的命名空间
env = os.environ.get("ENVIRONMENT", "dev")
os.environ["NACOS_NAMESPACE"] = env

# 方法2：使用不同的配置文件名
config_suffix = f"-{env}" if env != "prod" else ""
config = get_config(f"logger{config_suffix}.json")
```

## 📋 日志相关问题

### Q6: 火山引擎 TLS 日志发送失败？

**A**: 这是最常见的问题，按以下步骤排查：

1. **检查依赖**：
   ```bash
   pip show volcengine
   pip show lz4
   ```

2. **运行测试脚本**：
   ```bash
   python examples/test_tls_logging.py
   ```

3. **检查常见错误**：
   - `UnsupportedLZ4`: 缺少 lz4 依赖 → `pip install lz4`
   - `TopicNotExist`: TopicID 不存在或无权限
   - `SignatureDoesNotMatch`: AK/SK 错误

4. **验证配置**：
   ```python
   from nacos import get_config
   import json
   
   config = json.loads(get_config("tls.log.config"))
   print(f"Endpoint: {config.get('VOLCENGINE_ENDPOINT')}")
   print(f"Region: {config.get('VOLCENGINE_REGION')}")
   ```

### Q7: 日志中没有 TraceID？

**A**: 确保正确传入上下文：

```python
from context import create_context, set_context
from logger import get_logger

# 正确方式
ctx = create_context()
logger = get_logger("test")
logger.info(ctx, "这条日志会包含 TraceID")

# 错误方式
logger.info(None, "这条日志不会包含 TraceID")
```

### Q8: 如何自定义日志格式？

**A**: 在 Nacos 中修改 `logger.json` 配置：

```json
{
    "format": "%(asctime)s [%(trace_id)s] %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    "handlers": {
        "console": {"enabled": true}
    }
}
```

## 🌐 HTTP 客户端问题

### Q9: HTTP 请求超时怎么办？

**A**: 调整超时配置：

```python
from http_client import HTTPClient

# 方法1：创建客户端时设置
client = HTTPClient(timeout=60)

# 方法2：在 Nacos 中配置
# DataID: http.json
{
    "timeout": 60,
    "retry_count": 3
}
```

### Q10: 如何处理响应格式不统一的问题？

**A**: 使用标准响应格式：

```python
from http_client import create_response, ResponseCode
from context import get_current_context

# 统一响应格式
def api_handler():
    ctx = get_current_context()
    
    try:
        # 业务逻辑
        data = {"user_id": 123, "name": "John"}
        
        return create_response(
            context=ctx,
            code=ResponseCode.SUCCESS,
            data=data
        )
    except Exception as e:
        return create_response(
            context=ctx,
            code=ResponseCode.INTERNAL_ERROR,
            message=str(e)
        )
```

## 🔗 上下文管理问题

### Q11: 在异步代码中上下文丢失？

**A**: 确保在异步函数中正确设置上下文：

```python
import asyncio
from context import create_context, set_context, get_current_context

async def async_handler():
    # 在异步函数开始时设置上下文
    ctx = create_context()
    set_context(ctx)
    
    # 后续代码可以正常获取上下文
    await some_async_operation()
    
    current_ctx = get_current_context()
    print(f"TraceID: {current_ctx.trace_id}")

# 并发任务中每个任务都有独立上下文
async def main():
    tasks = []
    for i in range(5):
        task = asyncio.create_task(async_handler())
        tasks.append(task)
    
    await asyncio.gather(*tasks)
```

### Q12: 如何在跨服务调用中传递 TraceID？

**A**: 在 HTTP 请求头中传递：

```python
import requests
from context import get_current_context

def call_downstream_service():
    ctx = get_current_context()
    
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

## 🎯 服务注册发现问题

### Q13: 服务注册失败？

**A**: 检查以下配置：

1. **确认 Nacos 连接正常**
2. **检查服务配置**：
   ```python
   from nacos import init_service_manager, register_service
   
   # 初始化服务管理器
   init_service_manager()
   
   # 注册服务
   success = register_service(
       service_name="my-service",
       ip="192.168.1.100",  # 确保 IP 正确
       port=8080,           # 确保端口正确
       metadata={"version": "1.0.0"}
   )
   
   if not success:
       print("服务注册失败")
   ```

### Q14: 服务发现找不到实例？

**A**: 检查服务名称和健康状态：

```python
from nacos import discover_service, get_healthy_instances

# 检查所有实例
all_instances = discover_service("my-service")
print(f"所有实例数: {len(all_instances)}")

# 检查健康实例
healthy_instances = get_healthy_instances("my-service")
print(f"健康实例数: {len(healthy_instances)}")

# 如果健康实例为0，检查健康检查配置
```

## 🔧 性能优化问题

### Q15: SDK 性能影响如何？

**A**: SDK 设计时考虑了性能：

1. **日志异步发送**: TLS 日志不会阻塞主线程
2. **配置缓存**: 配置会被缓存，减少网络请求
3. **连接复用**: HTTP 客户端复用连接

监控性能指标：
```python
import time
from logger import get_logger
from context import create_context

logger = get_logger("performance")
ctx = create_context()

start_time = time.time()
# 执行业务逻辑
end_time = time.time()

logger.info(ctx, "操作完成", extra={
    "duration_ms": int((end_time - start_time) * 1000)
})
```

### Q16: 内存使用过高？

**A**: 检查以下几点：

1. **上下文对象**: 确保不持有大量上下文对象引用
2. **日志缓冲**: TLS 日志有内部缓冲，正常情况下会自动清理
3. **配置缓存**: 配置缓存有 TTL，会自动过期

```python
# 检查内存使用
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
```

## 🐛 故障排查

### Q17: 如何开启调试模式？

**A**: 设置日志级别为 DEBUG：

```python
from logger import init_logger_manager

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

### Q18: 如何查看详细错误信息？

**A**: 使用异常日志记录：

```python
from logger import get_logger
from context import create_context

logger = get_logger("error")
ctx = create_context()

try:
    # 可能出错的代码
    risky_operation()
except Exception as e:
    # 记录详细异常信息
    logger.exception(ctx, "操作失败", extra={
        "operation": "risky_operation",
        "error_type": type(e).__name__
    })
```

### Q19: 如何验证配置是否生效？

**A**: 使用配置验证工具：

```python
from nacos import get_config
import json

def verify_config():
    """验证配置是否正确"""
    configs = ["logger.json", "http.json", "tls.log.config"]
    
    for config_name in configs:
        try:
            config_str = get_config(config_name)
            config = json.loads(config_str)
            print(f"✅ {config_name}: 配置正常")
            print(f"   内容: {json.dumps(config, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ {config_name}: 配置错误 - {e}")

verify_config()
```

## 📞 获取帮助

### Q20: 如何获得更多帮助？

**A**: 可以通过以下方式：

1. **查看示例代码**: `examples/` 目录下有完整示例
2. **阅读详细文档**: 
   - [上下文管理](./context.md)
   - [日志管理](./logger.md)
   - [HTTP 客户端](./http_client.md)
   - [Nacos 服务发现](./nacos.md)
3. **运行测试脚本**: 验证功能是否正常
4. **联系开发团队**: 提交 Issue 或联系技术支持

### 问题反馈模板

报告问题时请提供以下信息：

```
**环境信息**:
- Python 版本: 
- SDK 版本: 
- 操作系统: 

**问题描述**:
详细描述遇到的问题

**复现步骤**:
1. 步骤1
2. 步骤2
3. ...

**期望结果**:
期望的正确行为

**实际结果**:
实际发生的错误

**错误日志**:
```
相关的错误日志
```

**配置信息**:
相关的配置内容（请移除敏感信息）
``` 