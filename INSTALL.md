# py-sdk 安装和使用指南

## 🚀 快速安装

### 方式1: Git Clone + pip install（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/py-sdk.git
cd py-sdk

# 2. 安装包（开发模式）
pip install -e .

# 3. 安装可选依赖（根据需要）
pip install -e .[all]  # 安装所有功能
pip install -e .[tls]  # 仅安装 TLS 支持
pip install -e .[web]  # 仅安装 Web 框架支持
```

### 方式2: 直接 pip 安装（如果已发布到 PyPI）

```bash
# 基础安装
pip install py-sdk

# 完整安装
pip install py-sdk[all]
```

## 📦 依赖说明

### 基础依赖（自动安装）
- `requests>=2.32.4` - HTTP 请求库
- `urllib3>=1.26.20,<3.0.0` - HTTP 客户端
- `contextvars>=2.4` - 上下文变量支持
- `python-dotenv>=0.19.0` - 环境变量管理

### 可选依赖组

#### `[tls]` - 火山引擎 TLS 支持
```bash
pip install py-sdk[tls]
```
包含：
- `volcengine>=1.0.184` - 火山引擎 SDK
- `lz4>=4.0.0` - LZ4 压缩库

#### `[web]` - Web 框架支持
```bash
pip install py-sdk[web]
```
包含：
- `fastapi>=0.68.0` - FastAPI 框架
- `uvicorn>=0.15.0` - ASGI 服务器
- `flask>=2.0.0` - Flask 框架
- `django>=3.2.0` - Django 框架
- `tornado>=6.0.0` - Tornado 框架

#### `[dev]` - 开发工具
```bash
pip install py-sdk[dev]
```
包含：
- `pytest>=6.0.0` - 测试框架
- `pytest-asyncio>=0.18.0` - 异步测试支持
- `pytest-cov>=2.12.0` - 覆盖率测试
- `black>=21.0.0` - 代码格式化
- `flake8>=3.9.0` - 代码检查
- `mypy>=0.910` - 类型检查

#### `[all]` - 所有功能
```bash
pip install py-sdk[all]
```
包含所有上述依赖。

## 🔧 环境配置

### 自动配置（推荐）

使用提供的自动化脚本：

```bash
# Windows (PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup-env.ps1

# Linux/Mac
chmod +x setup-env.sh
./setup-env.sh
```

### 手动配置

1. 复制环境变量模板：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件，设置必要的环境变量：
```bash
# Nacos 配置
NACOS_SERVER_ADDRESSES=127.0.0.1:8848
NACOS_NAMESPACE=dev
NACOS_USERNAME=nacos
NACOS_PASSWORD=nacos

# 火山引擎 TLS 配置（可选）
VOLCENGINE_ENDPOINT=https://tls-cn-beijing.volces.com
VOLCENGINE_ACCESS_KEY_ID=your-ak
VOLCENGINE_ACCESS_KEY_SECRET=your-sk
VOLCENGINE_REGION=cn-beijing
```

3. 加载环境变量：
```bash
# Linux/Mac
source .env

# Windows
# 或者直接在系统中设置环境变量
```

## 🎯 验证安装

### 基础功能测试

```python
# test_installation.py
from context import create_context
from logger import get_logger

# 创建上下文
ctx = create_context()
print(f"TraceID: {ctx.trace_id}")

# 获取日志记录器
logger = get_logger("test")
logger.info(ctx, "py-sdk 安装成功！")
```

### 运行示例代码

```bash
# 快速开始示例
python examples/package_usage_example.py

# 基础功能示例
python examples/basic_usage.py

# FastAPI 集成示例
python examples/fastapi_example.py
```

## 📝 使用方式

### 标准导入方式

```python
# 推荐：从各模块导入
from context import create_context
from logger import get_logger
from http_client import create_response

# 或者：导入整个模块
import context
import logger
import http_client
```

### 在其他项目中使用

1. **项目结构**：
```
your-project/
├── py-sdk/          # git clone 的 SDK 目录
├── your_app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── README.md
```

2. **安装 SDK**：
```bash
cd your-project
git clone https://github.com/your-org/py-sdk.git
cd py-sdk
pip install -e .
```

3. **在代码中使用**：
```python
# your_app/main.py
from context import create_context
from logger import get_logger

def main():
    ctx = create_context()
    logger = get_logger("your-app")
    logger.info(ctx, "应用启动")
```

## 🔍 常见问题

### Q1: 导入失败怎么办？
```bash
# 检查是否正确安装
pip list | grep py-sdk

# 重新安装
pip uninstall py-sdk
pip install -e .
```

### Q2: 缺少可选依赖？
```bash
# 安装特定功能
pip install py-sdk[tls]  # TLS 支持
pip install py-sdk[web]  # Web 框架支持
pip install py-sdk[all]  # 所有功能
```

### Q3: 环境变量配置问题？
```bash
# 检查环境变量
echo $NACOS_SERVER_ADDRESSES

# 重新运行配置脚本
./setup-env.sh
```

### Q4: 在 Docker 中使用？
```dockerfile
FROM python:3.9

WORKDIR /app

# 复制 SDK
COPY py-sdk/ ./py-sdk/

# 安装 SDK
RUN cd py-sdk && pip install -e .

# 复制应用代码
COPY . .

# 设置环境变量
ENV NACOS_SERVER_ADDRESSES=nacos:8848
ENV NACOS_NAMESPACE=prod

CMD ["python", "main.py"]
```

## 🚀 下一步

1. 查看 [完整文档](docs/README.md)
2. 运行 [示例代码](examples/)
3. 阅读 [API 文档](docs/)
4. 查看 [常见问题](docs/faq.md)

## 🆘 获取帮助

- 📚 文档：[docs/](docs/)
- 💬 问题：[GitHub Issues](https://github.com/your-org/py-sdk/issues)
- 📧 邮箱：your-email@example.com 