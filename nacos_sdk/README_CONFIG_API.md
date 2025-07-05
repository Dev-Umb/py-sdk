# Nacos配置获取API

这个模块提供了一个简单易用的Nacos配置获取API，无需手动初始化客户端。

## 特性

- **自动初始化**: 模块导入时自动初始化Nacos客户端
- **简单易用**: 只需调用`get_config()`函数即可获取配置
- **预配置服务器**: 已预配置Nacos服务器地址(`59.110.114.37:8848`)
- **无需鉴权**: 适用于无鉴权的Nacos环境
- **错误处理**: 内置完善的错误处理和日志记录

## 快速开始

### 基本用法

```python
from nacos import get_config

# 获取默认分组的配置
config = get_config("application.properties")
if config:
    print("配置内容:", config)
else:
    print("配置不存在")
```

### 指定分组

```python
from nacos import get_config

# 获取指定分组的配置
config = get_config("database.yml", "DEV_GROUP")
if config:
    print("数据库配置:", config)
```

### JSON配置处理

```python
import json
from nacos import get_config

# 获取JSON格式的配置
config_str = get_config("service.json")
if config_str:
    try:
        config = json.loads(config_str)
        print("服务配置:", config)
    except json.JSONDecodeError:
        print("配置格式错误")
```

## API参考

### get_config(data_id, group="DEFAULT_GROUP")

获取Nacos配置内容。

**参数:**
- `data_id` (str): 配置的dataId，必填
- `group` (str): 配置的分组名，默认为"DEFAULT_GROUP"

**返回值:**
- `str`: 配置内容字符串
- `None`: 配置不存在或获取失败

**示例:**
```python
# 获取默认分组配置
config = get_config("app.properties")

# 获取指定分组配置  
config = get_config("db.properties", "PROD_GROUP")
```

## 配置信息

- **Nacos服务器**: `59.110.114.37:8848`
- **命名空间**: 默认命名空间（空字符串）
- **鉴权**: 无需鉴权
- **超时时间**: 10秒

## 日志

模块使用Python标准logging模块记录日志，logger名称为`nacos-api`。

日志级别说明：
- `INFO`: 成功获取配置、客户端初始化
- `WARNING`: 配置不存在
- `ERROR`: 获取配置失败、网络异常等

启用日志：
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 运行示例

```bash
python nacos/example.py
```

## 错误处理

API内置了完善的错误处理：

1. **网络超时**: 10秒超时，返回None
2. **配置不存在**: 返回None，记录WARNING日志
3. **服务器错误**: 返回None，记录ERROR日志
4. **其他异常**: 返回None，记录异常信息

## 注意事项

1. 模块导入时会自动初始化客户端，首次导入可能有轻微延迟
2. 配置内容以字符串形式返回，需要根据实际格式进行解析
3. 当前版本使用固定的服务器地址，如需修改请编辑`nacos/api.py`文件
4. 建议在生产环境中添加适当的错误处理和重试机制 