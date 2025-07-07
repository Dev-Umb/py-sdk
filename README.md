# py_sdk - Python 微服务通用 SDK

一个为 Python 微服务开发设计的通用工具包，提供统一的日志管理、HTTP 客户端、上下文管理和服务注册发现等功能。

## 🚀 核心特性

- **🔗 上下文管理**: 自动生成和传递 TraceID，实现完整的链路追踪
- **📋 统一日志**: 结构化日志记录，自动包含 TraceID，支持火山引擎 TLS
- **🌐 HTTP 响应**: 标准化的 API 响应格式，统一的业务状态码系统
- **🎯 服务发现**: 基于 Nacos 的服务注册发现和配置管理
- **⚡ 开箱即用**: 零配置启动，极简的 API 设计

## 📦 快速安装

```bash
# 克隆项目
git clone <your-repo-url>
cd py_sdk

# 安装依赖
pip install -e .

# 安装可选功能
pip install -e .[all]  # 完整功能
pip install -e .[tls]  # 仅火山引擎 TLS 支持
```

## ⚡ 快速开始

### 3 行代码开始使用

```python
from context import create_context
from logger import get_logger

# 创建上下文（自动生成 TraceID）
ctx = create_context()

# 记录日志（自动包含 TraceID）
logger = get_logger("my-service")
logger.info(ctx, "服务启动成功")

# 输出: 2025-01-03 18:40:00,123 - my-service - INFO - [abc123def456] - 服务启动成功
```

### 完整功能演示

```python
from context import create_context
from logger import init_logger_manager, get_logger
from http_client import create_response, OK
from nacos_sdk import registerNacos

# 1. 初始化日志
init_logger_manager(service_name="my-service")

# 2. 注册服务
registerNacos(
    service_name="my-service",
    port=8080,
    metadata={"version": "1.0.0"}
)

# 3. 处理业务逻辑
ctx = create_context()
logger = get_logger("my-service")

logger.info(ctx, "处理用户请求", extra={"user_id": 123})

# 4. 创建标准响应
response = create_response(
    context=ctx,
    code=OK,
    data={"user_id": 123, "name": "张三"}
)
```

## 🛠 核心模块

### 1. 上下文管理 (context)

自动生成和管理 TraceID，实现链路追踪。

```python
from context import create_context, get_trace_id

# 创建上下文
ctx = create_context()
print(f"TraceID: {ctx.trace_id}")

# 获取当前 TraceID
trace_id = get_trace_id()
```

**📖 详细文档**: [docs/context.md](docs/context.md)  
**🔧 示例代码**: [examples/context_example.py](examples/context_example.py)

### 2. 日志管理 (logger)

统一的日志记录，自动包含 TraceID，支持多种输出方式。

```python
from logger import get_logger, init_logger_manager

# 初始化（可选）
init_logger_manager()

# 记录日志
logger = get_logger("my-service")
logger.info(ctx, "用户登录", extra={"user_id": 123})
```

**📖 详细文档**: [docs/logger.md](docs/logger.md)  
**🔧 示例代码**: [examples/logger_example.py](examples/logger_example.py)

### 3. HTTP 客户端 (http_client)

标准化的 HTTP 响应格式，统一的业务状态码系统。

```python
from http_client import create_response, OK, INVALID_PARAMS

# 成功响应
response = create_response(
    context=ctx,
    data={"id": 123, "name": "张三"}
)

# 错误响应
error = create_response(
    context=ctx,
    code=INVALID_PARAMS
)
```

**📖 详细文档**: [docs/http_client.md](docs/http_client.md)  
**🔧 示例代码**: [examples/http_client_example.py](examples/http_client_example.py)

### 4. 服务发现 (nacos_sdk)

基于 Nacos 的服务注册发现和配置管理。

```python
from nacos_sdk import registerNacos, get_config

# 注册服务
registerNacos(
    service_name="my-service",
    port=8080,
    metadata={"version": "1.0.0"}
)

# 获取配置
config = get_config("database.yml")
```

**📖 详细文档**: [docs/nacos_sdk.md](docs/nacos_sdk.md)  
**🔧 示例代码**: [examples/nacos_sdk_example.py](examples/nacos_sdk_example.py)

## 🎯 完整示例

查看完整的集成使用示例：

```bash
# 运行完整示例
python examples/complete_example.py
```

**🔧 完整示例**: [examples/complete_example.py](examples/complete_example.py)

## 🔧 环境配置

### 环境变量

```bash
# Nacos 配置
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848
export NACOS_NAMESPACE=dev
export NACOS_USERNAME=nacos
export NACOS_PASSWORD=nacos

# 火山引擎 TLS 配置（可选）
export VOLCENGINE_ENDPOINT=https://tls-cn-beijing.volces.com
export VOLCENGINE_ACCESS_KEY_ID=your-ak
export VOLCENGINE_ACCESS_KEY_SECRET=your-sk
export VOLCENGINE_REGION=cn-beijing
```

### 快速配置脚本

```bash
# Windows
.\setup-env.ps1

# Linux/Mac
chmod +x setup-env.sh
./setup-env.sh
```

## 🌐 Web 框架集成

### FastAPI

```python
from fastapi import FastAPI, Request
from context import create_context_from_request
from http_client import create_response, OK

app = FastAPI()

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, request: Request):
    ctx = create_context_from_request(request)
    
    # 业务逻辑
    user_data = {"id": user_id, "name": "张三"}
    
    return create_response(
        context=ctx,
        code=OK,
        data=user_data
    ).to_dict()
```

### Flask

```python
from flask import Flask, request
from context import create_context_from_request
from http_client import create_response, OK

app = Flask(__name__)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    ctx = create_context_from_request(request)
    
    # 业务逻辑
    user_data = {"id": user_id, "name": "张三"}
    
    response = create_response(
        context=ctx,
        code=OK,
        data=user_data
    )
    return response.to_dict()
```

## 📋 依赖要求

### 基础依赖（自动安装）

- `requests>=2.32.4` - HTTP 请求库
- `urllib3>=1.26.20,<3.0.0` - HTTP 客户端
- `contextvars>=2.4` - 上下文变量支持
- `python-dotenv>=0.19.0` - 环境变量管理

### 可选依赖

```bash
# 火山引擎 TLS 支持
pip install py_sdk[tls]

# Web 框架支持
pip install py_sdk[web]

# 开发工具
pip install py_sdk[dev]

# 完整功能
pip install py_sdk[all]
```

## 🌟 最佳实践

### 1. 项目结构

```
your-project/
├── main.py                 # 应用入口
├── config/
│   ├── __init__.py
│   └── settings.py         # 配置管理
├── services/
│   ├── __init__.py
│   ├── user_service.py     # 业务服务
│   └── order_service.py
├── api/
│   ├── __init__.py
│   └── routes.py          # API 路由
└── requirements.txt
```

### 2. 应用初始化

```python
# main.py
from context import create_context
from logger import init_logger_manager, get_logger
from nacos_sdk import registerNacos
from http_client import create_response, OK

# 初始化日志
init_logger_manager(service_name="my-app")

# 注册服务
registerNacos(
    service_name="my-app",
    port=8080,
    metadata={"version": "1.0.0"}
)

logger = get_logger(__name__)
ctx = create_context()
logger.info(ctx, "应用启动成功")
```

### 3. 业务服务

```python
# services/user_service.py
from context import get_current_context
from logger import get_logger
from http_client import create_response, OK, INVALID_PARAMS

logger = get_logger(__name__)

def get_user_by_id(user_id):
    ctx = get_current_context()
    
    logger.info(ctx, "查询用户", extra={"user_id": user_id})
    
    if user_id <= 0:
        return create_response(
            context=ctx,
            code=INVALID_PARAMS
        )
    
    # 业务逻辑
    user_data = {"id": user_id, "name": "张三"}
    
    return create_response(
        context=ctx,
        code=OK,
        data=user_data
    )
```

### 4. 错误处理

```python
from http_client import create_response, INTERNAL_SERVER_ERROR

try:
    # 业务逻辑
    result = process_business_logic()
    return create_response(context=ctx, data=result)
    
except Exception as e:
    logger.exception(ctx, "业务处理异常", extra={"error": str(e)})
    return create_response(
        context=ctx,
        code=INTERNAL_SERVER_ERROR
    )
```

## 📚 更多文档

- **[安装指南](INSTALL.md)** - 详细的安装和配置说明
- **[更新日志](CHANGELOG.md)** - 版本更新记录
- **[贡献指南](CONTRIBUTING.md)** - 如何参与项目开发

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 支持

如有问题或建议，请：

1. 查看 [FAQ 文档](docs/faq.md)
2. 提交 [Issue](https://github.com/your-org/py-sdk/issues)
3. 发起 [Pull Request](https://github.com/your-org/py-sdk/pulls)

---

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！** 