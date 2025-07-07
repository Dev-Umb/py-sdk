import logging
import os
import requests
from typing import Optional

logger = logging.getLogger("nacos-api")

class NacosConfigClient:
    """Nacos配置管理客户端"""
    
    def __init__(self, server_address: str, namespace: str = ""):
        """
        初始化Nacos配置客户端
        
        Args:
            server_address: Nacos服务器地址，格式为 "ip:port"
            namespace: 命名空间ID，默认为空
        """
        self.server_address = server_address
        self.namespace = namespace
        self.base_url = f"http://{server_address}/nacos/v1/cs/configs"
        logger.info(f"初始化Nacos配置客户端: {server_address}, namespace: {namespace}")
    
    def get_config(self, data_id: str, group: str = "DEFAULT_GROUP") -> Optional[str]:
        """
        获取配置内容
        
        Args:
            data_id: 配置的dataId
            group: 配置的分组，默认为DEFAULT_GROUP
            
        Returns:
            配置内容字符串，如果获取失败返回None
        """
        try:
            params = {
                "dataId": data_id,
                "group": group
            }
            
            # 如果有命名空间，添加到参数中
            if self.namespace:
                params["tenant"] = self.namespace
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                config_content = response.text
                logger.info(f"成功获取配置: dataId={data_id}, group={group}")
                return config_content
            elif response.status_code == 404:
                logger.warning(f"配置不存在: dataId={data_id}, group={group}")
                return None
            else:
                logger.error(f"获取配置失败: status={response.status_code}, text={response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"获取配置超时: dataId={data_id}, group={group}")
            return None
        except Exception as e:
            logger.error(f"获取配置异常: {str(e)}")
            return None


# 全局配置客户端实例
_config_client: Optional[NacosConfigClient] = None

def _init_client():
    """初始化全局配置客户端"""
    global _config_client
    if _config_client is None:
        # 从环境变量读取配置
        server_addresses = os.getenv('NACOS_ADDRESS', '127.0.0.1:8848')
        namespace = os.getenv('NACOS_NAMESPACE', '')
        
        # 如果有多个地址，取第一个作为配置客户端地址
        server_address = server_addresses.split(',')[0].strip()
        
        _config_client = NacosConfigClient(server_address, namespace)
        logger.info("Nacos配置客户端已初始化")

def get_config(data_id: str, group: str = "DEFAULT_GROUP") -> Optional[str]:
    """
    获取Nacos配置
    
    Args:
        data_id: 配置的dataId
        group: 配置的分组，默认为DEFAULT_GROUP
        
    Returns:
        配置内容字符串，如果获取失败返回None
        
    Example:
        >>> from nacos_sdk.api import get_config
        >>> config = get_config("database.properties", "DEFAULT_GROUP")
        >>> if config:
        >>>     print(config)
    """
    # 确保客户端已初始化
    if _config_client is None:
        _init_client()
    
    return _config_client.get_config(data_id, group)

# 模块导入时自动初始化
_init_client() 