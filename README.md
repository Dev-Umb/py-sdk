# Python 微服务通用 SDK (py-sdk)

一个为 Python 微服务开发设计的通用工具包，提供统一的日志管理、HTTP 客户端、上下文管理和服务注册发现等功能。

## 🚀 核心特性

- **🔧 零配置启动**: 所有配置通过 Nacos 自动获取，开箱即用
- **📋 统一日志**: 自动包含 TraceID 的结构化日志，支持火山引擎 TLS
- **🌐 HTTP 客户端**: 标准化的 HTTP 请求和响应处理
- **🔗 上下文管理**: 自动 TraceID 传递，支持异步安全
- **🎯 服务发现**: 基于 Nacos 的服务注册与发现
- **📊 可观测性**: 完整的链路追踪和日志聚合

## 📦 快速安装

```bash
# 克隆项目
git clone <your-repo-url>
cd py-sdk

# 安装依赖
pip install -r requirements.txt

# 安装火山引擎 TLS 支持（可选）
pip install lz4>=4.0.0
```

## ⚡ 快速开始

### 最简使用（3行代码）

```python
from context import create_context
from logger import get_logger

# 创建上下文（自动生成 TraceID）
ctx = create_context()

# 获取日志记录器并记录日志
logger = get_logger("my-service")
logger.info(ctx, "服务启动成功")

# 输出: 2025-07-03 18:40:00,123 - my-service - INFO - [abc123def456] - 服务启动成功
```

### 完整功能使用

```python
from context import create_context
from logger import init_logger_manager, get_logger
from http_client import create_response, ResponseCode
from nacos import registerNacos

# 1. 初始化日志（支持火山引擎 TLS）
init_logger_manager(
    config={"handlers": {"tls": {"enabled": True}}},
    topic_id="your-tls-topic-id",
    service_name="my-service"
)

# 2. 注册服务（使用环境变量配置）
success = registerNacos(
    service_name="my-service",
    port=8080,
    # server_addresses, namespace, username, password 从环境变量读取
    metadata={"version": "1.0.0"}
)

# 3. 使用上下文和日志
ctx = create_context()
logger = get_logger("my-service")

logger.info(ctx, "服务已启动", extra={
    "port": 8080,
    "version": "1.0.0",
    "nacos_registered": success
})

# 4. 创建标准响应
response = create_response(
    context=ctx,
    code=ResponseCode.SUCCESS,
    data={"message": "Hello World"}
)
```

## 🛠 工具库概览

### 1. 上下文管理 (context)
- **作用**: 管理请求上下文和 TraceID，实现链路追踪
- **核心功能**: 自动生成 TraceID，上下文传递，异步安全

### 2. 日志管理 (logger)  
- **作用**: 统一的日志记录，自动包含 TraceID
- **核心功能**: 多种输出方式（控制台、文件、火山引擎 TLS），结构化日志

### 3. HTTP 客户端 (http_client)
- **作用**: 标准化的 HTTP 请求处理和响应格式
- **核心功能**: 统一响应格式，中间件支持，错误处理

### 4. 服务发现 (nacos)
- **作用**: 基于 Nacos 的配置管理和服务注册发现
- **核心功能**: 配置热更新，服务注册，健康检查

## 🔧 环境配置

### 快速配置

**方式1：使用自动化脚本（推荐）**

```bash
# Windows (PowerShell) - 首次运行需要设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup-env.ps1

# Linux/Mac
chmod +x setup-env.sh
./setup-env.sh
```

**方式2：手动配置**

```bash
# 1. 复制环境变量示例文件
cp env.example .env

# 2. 编辑配置文件
vim .env  # 或使用其他编辑器

# 3. 设置必要的环境变量
source .env  # Linux/Mac
# 或直接在系统中设置环境变量
```

### Nacos 配置

```bash
# 环境变量方式（推荐）
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848  # 支持多地址: "ip1:port1,ip2:port2"
export NACOS_NAMESPACE=dev
export NACOS_USERNAME=nacos  # 可选
export NACOS_PASSWORD=nacos  # 可选
```

**环境变量说明**：
- `NACOS_SERVER_ADDRESSES`: Nacos服务器地址，支持集群配置
- `NACOS_NAMESPACE`: 命名空间，用于环境隔离
- `NACOS_USERNAME`: 认证用户名（启用认证时必需）
- `NACOS_PASSWORD`: 认证密码（启用认证时必需）

**配置优先级**：参数 > 环境变量 > 默认值（127.0.0.1:8848）

> 📋 **完整配置列表**：查看 [`env.example`](./env.example) 文件获取所有支持的环境变量配置项

### 火山引擎 TLS 配置

在 Nacos 中创建配置：

**DataID**: `tls.log.config`  
**Group**: `DEFAULT_GROUP`

```json
{
    "VOLCENGINE_ENDPOINT": "https://tls-cn-beijing.volces.com",
    "VOLCENGINE_ACCESS_KEY_ID": "your-ak",
    "VOLCENGINE_ACCESS_KEY_SECRET": "your-sk",
    "VOLCENGINE_REGION": "cn-beijing"
}
```

## 🎯 示例代码

查看 `examples/` 目录下的完整示例：

```bash
# 基础功能演示
python examples/basic_usage.py

# FastAPI 集成示例
python examples/fastapi_example.py

# 火山引擎 TLS 日志测试
python examples/test_tls_logging.py

# Nacos 环境变量配置示例
python examples/nacos_env_example.py

# 环境变量配置使用示例
python examples/env_config_example.py

# Nacos 连接测试
python examples/nacos_connection_example.py
```

## 📚 详细文档

完整的使用文档位于 `docs/` 目录：

- **[快速开始指南](./docs/README.md)** - 完整的 SDK 使用指南
- **[上下文管理](./docs/context.md)** - TraceID 和上下文管理
- **[日志管理](./docs/logger.md)** - 日志记录和火山引擎 TLS 集成
- **[HTTP 客户端](./docs/http_client.md)** - HTTP 请求和响应处理
- **[Nacos 服务发现](./docs/nacos.md)** - 配置管理和服务注册发现
- **[配置管理指南](./docs/config.md)** - 配置文件和环境变量
- **[常见问题解答](./docs/faq.md)** - 问题排查和解决方案

## 🚨 注意事项

1. **TopicID 必需**: 使用火山引擎 TLS 时，每个服务必须配置不同的 TopicID
2. **依赖安装**: 火山引擎 TLS 需要安装 `lz4>=4.0.0` 依赖
3. **异步安全**: 所有上下文操作都是异步安全的
4. **配置热更新**: Nacos 配置支持热更新，无需重启服务

## 📞 技术支持

如有问题，请查看：
1. [常见问题解答](./docs/faq.md)
2. [配置指南](./docs/config.md)
3. 示例代码 `examples/`
4. 提交 Issue 或联系开发团队

---

**开始使用**: 查看 [完整文档](./docs/README.md) 了解详细的使用方法和最佳实践。 