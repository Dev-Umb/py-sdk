# Nacos配置获取API - 使用说明

## 快速开始

这个API已经预配置了Nacos服务器地址 `59.110.114.37:8848`，无需手动初始化，直接使用即可。

### 基本使用

```python
from nacos.api import get_config

# 获取默认分组的配置
config = get_config("application.properties")
if config:
    print("配置内容:", config)
else:
    print("配置不存在")
```

### 指定分组

```python
from nacos.api import get_config

# 获取指定分组的配置
config = get_config("database.yml", "DEV_GROUP")
if config:
    print("数据库配置:", config)
```

### 处理JSON配置

```python
import json
from nacos.api import get_config

config_str = get_config("service.json")
if config_str:
    try:
        config = json.loads(config_str)
        print("解析后的配置:", config)
    except json.JSONDecodeError:
        print("配置格式错误")
```

## API说明

### get_config(data_id, group="DEFAULT_GROUP")

**参数:**
- `data_id`: 配置ID（必填）
- `group`: 分组名（可选，默认为"DEFAULT_GROUP"）

**返回:**
- 成功: 配置内容字符串
- 失败: `None`

## 配置信息

- **服务器**: 59.110.114.37:8848
- **命名空间**: 默认（空）
- **鉴权**: 无
- **超时**: 10秒

## 注意事项

1. 模块导入时自动初始化，首次使用可能有轻微延迟
2. 返回的配置内容为字符串，需根据格式自行解析
3. 网络异常或配置不存在时返回 `None` 