# 配置管理指南

本文档详细说明了 py-sdk 的配置管理方式和各模块的配置选项。

## 🎯 配置优先级

配置加载的优先级顺序（从高到低）：

1. **环境变量** - 最高优先级
2. **Nacos 配置中心** - 中等优先级  
3. **默认配置** - 最低优先级

## 🔧 环境变量配置

### Nacos 连接配置

```bash
# Nacos 服务器地址（必需）- 支持多地址，逗号分隔
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848

# Nacos 命名空间（可选，默认为空）
export NACOS_NAMESPACE=dev

# Nacos 认证信息（可选）
export NACOS_USERNAME=nacos
export NACOS_PASSWORD=nacos

# SDK 自动初始化开关（可选，默认为 true）
export PY_SDK_AUTO_INIT=true
```

**环境变量说明**：
- `NACOS_SERVER_ADDRESSES`: Nacos服务器地址，支持集群配置（如：`ip1:port1,ip2:port2`）
- `NACOS_NAMESPACE`: 命名空间ID，用于环境隔离
- `NACOS_USERNAME`: 认证用户名（启用认证时必需）
- `NACOS_PASSWORD`: 认证密码（启用认证时必需）

**配置优先级**：参数 > 环境变量 > 默认值

### 快速配置示例

```bash
# 开发环境
export NACOS_SERVER_ADDRESSES=127.0.0.1:8848
export NACOS_NAMESPACE=dev

# 测试环境  
export NACOS_SERVER_ADDRESSES=test-nacos.example.com:8848
export NACOS_NAMESPACE=test

# 生产环境（集群配置）
export NACOS_SERVER_ADDRESSES=prod-nacos1.example.com:8848,prod-nacos2.example.com:8848
export NACOS_NAMESPACE=prod
export NACOS_USERNAME=prod_user
export NACOS_PASSWORD=secure_password
```

## 📋 Nacos 配置文件

所有配置文件都存储在 Nacos 配置中心，Group 为 `DEFAULT_GROUP`。

### 1. 日志配置 (logger.json)

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

#### 配置项说明

- `level`: 全局日志级别 (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `format`: 日志格式字符串，支持 TraceID 占位符
- `handlers`: 日志处理器配置

**控制台处理器 (console)**:
- `enabled`: 是否启用控制台输出
- `level`: 控制台日志级别

**文件处理器 (file)**:
- `enabled`: 是否启用文件输出
- `level`: 文件日志级别
- `filename`: 日志文件名
- `max_bytes`: 单个日志文件最大大小（字节）
- `backup_count`: 保留的日志文件数量

**TLS 处理器 (tls)**:
- `enabled`: 是否启用火山引擎 TLS 输出
- `level`: TLS 日志级别

### 2. 火山引擎 TLS 配置 (tls.log.config)

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

#### 配置项说明

- `VOLCENGINE_ENDPOINT`: 火山引擎 TLS 服务端点
- `VOLCENGINE_ACCESS_KEY_ID`: 访问密钥 ID
- `VOLCENGINE_ACCESS_KEY_SECRET`: 访问密钥
- `VOLCENGINE_TOKEN`: 临时令牌（可选）
- `VOLCENGINE_REGION`: 服务区域

### 3. HTTP 配置 (http.json)

**DataID**: `http.json`  
**Group**: `DEFAULT_GROUP`

```json
{
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1,
    "max_retry_delay": 60,
    "default_headers": {
        "User-Agent": "py-sdk/1.0.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    "response_format": {
        "success_code": 200,
        "error_code": 500,
        "include_trace_id": true,
        "include_timestamp": true
    },
    "circuit_breaker": {
        "enabled": true,
        "failure_threshold": 5,
        "recovery_timeout": 60
    }
}
```

#### 配置项说明

**基础配置**:
- `timeout`: 请求超时时间（秒）
- `retry_count`: 重试次数
- `retry_delay`: 重试延迟（秒）
- `max_retry_delay`: 最大重试延迟（秒）

**默认请求头**:
- `default_headers`: 所有请求的默认头部

**响应格式**:
- `success_code`: 默认成功响应码
- `error_code`: 默认错误响应码
- `include_trace_id`: 是否在响应中包含 TraceID
- `include_timestamp`: 是否在响应中包含时间戳

**熔断器配置**:
- `enabled`: 是否启用熔断器
- `failure_threshold`: 失败阈值
- `recovery_timeout`: 恢复超时时间

### 4. 服务注册配置 (services.json)

**DataID**: `services.json`  
**Group**: `DEFAULT_GROUP`

```json
{
    "services": [
        {
            "name": "user-service",
            "port": 8080,
            "health_check_url": "/health",
            "metadata": {
                "version": "1.0.0",
                "team": "backend",
                "environment": "production"
            }
        },
        {
            "name": "order-service", 
            "port": 8081,
            "health_check_url": "/api/health",
            "metadata": {
                "version": "1.0.0",
                "team": "backend",
                "environment": "production"
            }
        }
    ],
    "health_check": {
        "enabled": true,
        "interval": 30,
        "timeout": 5,
        "failure_threshold": 3
    }
}
```

#### 配置项说明

**服务配置**:
- `name`: 服务名称
- `port`: 服务端口
- `health_check_url`: 健康检查 URL
- `metadata`: 服务元数据

**健康检查配置**:
- `enabled`: 是否启用健康检查
- `interval`: 检查间隔（秒）
- `timeout`: 检查超时（秒）
- `failure_threshold`: 失败阈值

## 🔄 配置热更新

### 配置监听示例

```python
from nacos import add_config_listener
import json

def config_changed_handler(data_id, group, content):
    """配置变化处理器"""
    print(f"配置更新: {data_id}")
    
    try:
        config = json.loads(content)
        
        if data_id == "logger.json":
            # 重新初始化日志配置
            reinit_logger(config)
        elif data_id == "http.json":
            # 重新初始化 HTTP 配置
            reinit_http_client(config)
        elif data_id == "services.json":
            # 重新注册服务
            reregister_services(config)
            
    except Exception as e:
        print(f"配置更新失败: {e}")

# 添加配置监听器
add_config_listener("logger.json", "DEFAULT_GROUP", config_changed_handler)
add_config_listener("http.json", "DEFAULT_GROUP", config_changed_handler)
add_config_listener("services.json", "DEFAULT_GROUP", config_changed_handler)
```

## 🌍 多环境配置

### 环境隔离策略

```python
import os

def get_environment():
    """获取当前环境"""
    return os.environ.get("ENVIRONMENT", "dev")

def setup_nacos_config():
    """设置 Nacos 配置"""
    env = get_environment()
    
    if env == "dev":
        os.environ["NACOS_ADDRESS"] = "127.0.0.1:8848"
        os.environ["NACOS_NAMESPACE"] = "dev"
    elif env == "test":
        os.environ["NACOS_ADDRESS"] = "test-nacos.example.com:8848"
        os.environ["NACOS_NAMESPACE"] = "test"
    elif env == "prod":
        os.environ["NACOS_ADDRESS"] = "prod-nacos.example.com:8848"
        os.environ["NACOS_NAMESPACE"] = "prod"
        os.environ["NACOS_USERNAME"] = "prod_user"
        os.environ["NACOS_PASSWORD"] = "secure_password"

# 应用启动时设置配置
setup_nacos_config()
```

### 配置文件命名规范

```
# 开发环境
logger.json
http.json
services.json

# 测试环境  
logger-test.json
http-test.json
services-test.json

# 生产环境
logger-prod.json
http-prod.json
services-prod.json
```

## 🔐 敏感信息管理

### 配置加密

```python
import base64
from cryptography.fernet import Fernet

class ConfigEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        """加密配置"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密配置"""
        encrypted = base64.b64decode(encrypted_data.encode())
        return self.cipher.decrypt(encrypted).decode()

# 使用示例
encryption_key = os.environ.get("CONFIG_ENCRYPTION_KEY")
encryptor = ConfigEncryption(encryption_key)

# 加密敏感配置
sensitive_config = {
    "database_password": "secret_password",
    "api_key": "secret_api_key"
}
encrypted_config = encryptor.encrypt(json.dumps(sensitive_config))

# 存储到 Nacos
put_config("sensitive.json", encrypted_config)

# 读取并解密
encrypted_data = get_config("sensitive.json")
decrypted_config = json.loads(encryptor.decrypt(encrypted_data))
```

### 环境变量注入

```python
import os
import re

def resolve_env_vars(config_str: str) -> str:
    """解析配置中的环境变量"""
    def replace_env_var(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) else ""
        return os.environ.get(var_name, default_value)
    
    # 支持 ${VAR_NAME:default_value} 格式
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
    return re.sub(pattern, replace_env_var, config_str)

# 配置文件中使用环境变量
config_template = '''
{
    "database": {
        "host": "${DB_HOST:localhost}",
        "port": ${DB_PORT:3306},
        "password": "${DB_PASSWORD}"
    },
    "redis": {
        "host": "${REDIS_HOST:localhost}",
        "port": ${REDIS_PORT:6379}
    }
}
'''

# 解析环境变量
resolved_config = resolve_env_vars(config_template)
config = json.loads(resolved_config)
```

## 🛠 配置验证

### 配置模式验证

```python
import jsonschema

# 定义配置模式
LOGGER_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "level": {
            "type": "string",
            "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        },
        "format": {"type": "string"},
        "handlers": {
            "type": "object",
            "properties": {
                "console": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "level": {"type": "string"}
                    },
                    "required": ["enabled"]
                }
            }
        }
    },
    "required": ["level", "handlers"]
}

def validate_config(config: dict, schema: dict) -> bool:
    """验证配置格式"""
    try:
        jsonschema.validate(config, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"配置验证失败: {e}")
        return False

# 使用示例
config = json.loads(get_config("logger.json"))
if validate_config(config, LOGGER_CONFIG_SCHEMA):
    print("配置验证通过")
else:
    print("配置验证失败")
```

## 📊 配置最佳实践

### 1. 配置分层管理

```
configs/
├── base/              # 基础配置
│   ├── logger.json
│   ├── http.json
│   └── services.json
├── dev/               # 开发环境配置
│   ├── logger.json
│   └── database.json
├── test/              # 测试环境配置
│   ├── logger.json
│   └── database.json
└── prod/              # 生产环境配置
    ├── logger.json
    └── database.json
```

### 2. 配置版本管理

```python
def get_config_with_version(data_id: str, group: str = "DEFAULT_GROUP"):
    """获取带版本的配置"""
    config_str = get_config(data_id, group)
    config = json.loads(config_str)
    
    # 添加版本信息
    config["_meta"] = {
        "version": "1.0.0",
        "updated_at": time.time(),
        "updated_by": "system"
    }
    
    return config
```

### 3. 配置缓存策略

```python
import time
from typing import Dict, Any

class ConfigCache:
    def __init__(self, ttl: int = 300):  # 5分钟缓存
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, data_id: str, group: str = "DEFAULT_GROUP"):
        """获取缓存的配置"""
        cache_key = f"{group}:{data_id}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.ttl:
                return cached_data["config"]
        
        # 缓存过期或不存在，重新获取
        config = get_config(data_id, group)
        self.cache[cache_key] = {
            "config": config,
            "timestamp": time.time()
        }
        
        return config

# 使用配置缓存
config_cache = ConfigCache(ttl=300)
config = config_cache.get("logger.json")
```

## ⚠️ 注意事项

1. **敏感信息**: 不要在配置文件中明文存储密码、密钥等敏感信息
2. **配置备份**: 重要配置应该有备份和恢复机制
3. **权限控制**: 限制配置文件的访问权限
4. **变更记录**: 记录配置变更历史，便于问题追踪
5. **测试验证**: 配置变更前应该在测试环境验证

## 🔧 故障排查

### 常见问题

1. **Nacos 连接失败**
   ```bash
   # 检查网络连接
   telnet nacos-server 8848
   
   # 检查环境变量
   echo $NACOS_ADDRESS
   echo $NACOS_NAMESPACE
   ```

2. **配置获取失败**
   ```python
   # 检查配置是否存在
   try:
       config = get_config("logger.json")
       print("配置获取成功")
   except Exception as e:
       print(f"配置获取失败: {e}")
   ```

3. **配置格式错误**
   ```python
   # 验证 JSON 格式
   try:
       config = json.loads(config_str)
       print("JSON 格式正确")
   except json.JSONDecodeError as e:
       print(f"JSON 格式错误: {e}")
   ```