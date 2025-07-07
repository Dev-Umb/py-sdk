# Nacos SDK (nacos_sdk)

Nacos SDK 模块提供基于 Nacos 的服务注册发现和配置管理功能，支持自动心跳、健康检查和配置热更新。

## 📋 核心功能

- **服务注册发现**: 自动注册服务到 Nacos，支持服务发现
- **配置管理**: 从 Nacos 获取配置信息，支持热更新
- **健康检查**: 自动心跳机制，保持服务健康状态
- **环境变量支持**: 支持通过环境变量配置 Nacos 连接信息
- **集群支持**: 支持 Nacos 集群配置

## 🚀 快速开始

### 基础服务注册

```python
from nacos_sdk import registerNacos

# 注册服务（使用环境变量配置）
success = registerNacos(
    service_name="my-service",
    port=8080,
    metadata={"version": "1.0.0", "env": "prod"}
)

if success:
    print("服务注册成功")
else:
    print("服务注册失败")
```

### 环境变量配置

```bash
# 设置环境变量
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848
export NACOS_NAMESPACE=dev
export NACOS_USERNAME=nacos
export NACOS_PASSWORD=nacos
```

### 完整配置示例

```python
from nacos_sdk import registerNacos, get_config

# 注册服务（显式配置）
success = registerNacos(
    service_name="user-service",
    port=8080,
    server_addresses="127.0.0.1:8848,127.0.0.1:8849",
    namespace="production",
    username="nacos",
    password="nacos",
    metadata={
        "version": "1.0.0",
        "team": "backend",
        "env": "prod"
    }
)

# 获取配置
config = get_config("database.yml", "DEFAULT_GROUP")
if config:
    print(f"数据库配置: {config}")
```

## 📖 API 参考

### registerNacos(service_name, port, **kwargs)

注册服务到 Nacos。

**参数:**
- `service_name` (str, 必需): 服务名称
- `port` (int, 必需): 服务端口
- `server_addresses` (str, 可选): Nacos 服务器地址，默认从环境变量读取
- `namespace` (str, 可选): 命名空间，默认从环境变量读取
- `username` (str, 可选): 用户名，默认从环境变量读取
- `password` (str, 可选): 密码，默认从环境变量读取
- `metadata` (dict, 可选): 服务元数据
- `cluster_name` (str, 可选): 集群名称，默认 "DEFAULT"
- `group_name` (str, 可选): 分组名称，默认 "DEFAULT_GROUP"
- `ip` (str, 可选): 服务 IP，默认自动获取本机 IP

**返回:**
- `bool`: 注册是否成功

### unregisterNacos(service_name, port, **kwargs)

注销服务。

**参数:**
- `service_name` (str, 必需): 服务名称
- `port` (int, 必需): 服务端口
- `ip` (str, 可选): 服务 IP，默认自动获取
- `cluster_name` (str, 可选): 集群名称，默认 "DEFAULT"
- `group_name` (str, 可选): 分组名称，默认 "DEFAULT_GROUP"

**返回:**
- `bool`: 注销是否成功

### get_config(data_id, group="DEFAULT_GROUP")

从 Nacos 获取配置。

**参数:**
- `data_id` (str, 必需): 配置的 dataId
- `group` (str, 可选): 配置分组，默认 "DEFAULT_GROUP"

**返回:**
- `str`: 配置内容，如果不存在则返回 None

## 🔧 环境变量配置

### 基础配置

```bash
# Nacos 服务器地址（必需）
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848

# 命名空间（可选）
export NACOS_NAMESPACE=dev

# 认证信息（可选，如果 Nacos 启用了认证）
export NACOS_USERNAME=nacos
export NACOS_PASSWORD=nacos
```

### 集群配置

```bash
# 多个 Nacos 服务器
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848,127.0.0.1:8849,127.0.0.1:8850

# 生产环境命名空间
export NACOS_NAMESPACE=production
```

## 💡 使用示例

### 1. 服务注册与发现

```python
from nacos_sdk import registerNacos, unregisterNacos
import signal
import sys

def signal_handler(sig, frame):
    print("正在注销服务...")
    unregisterNacos("my-service", 8080)
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 注册服务
success = registerNacos(
    service_name="my-service",
    port=8080,
    metadata={
        "version": "1.0.0",
        "description": "我的微服务"
    }
)

if success:
    print("服务注册成功，开始提供服务...")
    # 你的服务逻辑
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
```

### 2. 配置管理

```python
from nacos_sdk import get_config
import json
import time
import threading

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_config()
        
        # 启动配置监听线程
        self.start_config_watcher()
    
    def load_config(self):
        """加载配置"""
        try:
            config_str = get_config("app.json")
            if config_str:
                self.config = json.loads(config_str)
                logger.info(create_context(), "配置加载成功", extra={
                    "config_keys": list(self.config.keys())
                })
        except Exception as e:
            logger.error(create_context(), "配置加载失败", extra={
                "error": str(e)
            })
    
    def start_config_watcher(self):
        """启动配置监听"""
        def watch_config():
            while True:
                try:
                    old_config = self.config.copy()
                    self.load_config()
                    
                    # 检查配置是否发生变化
                    if old_config != self.config:
                        logger.info(create_context(), "配置已更新")
                        self.on_config_changed()
                    
                    time.sleep(30)  # 每30秒检查一次
                    
                except Exception as e:
                    logger.error(create_context(), "配置监听异常", extra={
                        "error": str(e)
                    })
                    time.sleep(10)
        
        thread = threading.Thread(target=watch_config, daemon=True)
        thread.start()
    
    def on_config_changed(self):
        """配置变化回调"""
        # 在这里处理配置变化逻辑
        pass
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

# 使用配置管理器
config_manager = ConfigManager()
```

### 3. 服务发现

```python
from nacos_sdk import init_nacos_client, get_nacos_client

# 初始化 Nacos 客户端
init_nacos_client()

# 获取客户端实例
client = get_nacos_client()

if client:
    # 获取服务实例列表
    instances = client.get_service_instances("user-service")
    
    for instance in instances:
        print(f"服务实例: {instance['ip']}:{instance['port']}")
        print(f"元数据: {instance.get('metadata', {})}")
        print(f"健康状态: {instance.get('healthy', False)}")
```

## 🌟 最佳实践

1. **环境变量配置**: 使用环境变量管理不同环境的配置
2. **优雅关闭**: 在应用关闭时注销服务
3. **健康检查**: 利用 Nacos 的健康检查机制
4. **配置热更新**: 实现配置变化的监听和热更新
5. **服务元数据**: 合理使用元数据传递服务信息

## 🔗 相关模块

- [context](context.md) - 在服务调用中传递 TraceID
- [logger](logger.md) - 记录服务注册和配置变化日志
- [http_client](http_client.md) - 在微服务调用中使用标准响应格式 