import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger("nacos-config")

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 尝试从不同位置加载.env文件
    env_paths = ['./.env', '../.env', '/app/.env', '/app/rest/.env']
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"已从 {env_path} 加载环境变量配置")
            break
    else:
        logger.warning("未找到.env文件，将使用系统环境变量")
except ImportError:
    logger.warning("未安装python-dotenv，无法从.env文件加载配置")

# 默认的服务配置
DEFAULT_SERVICES = [
    # 客户端WebSocket服务
    {
        "name": "drama-ws-service",
        "port": 8000,
        "service_type": "ws",
        "protocols": ["websocket"],
        "metadata": {
            "service": "drama-ws",
            "version": "1.0.0"
        },
        "cluster": "DEFAULT",
        "group": "DEFAULT_GROUP"
    },
    # DS服务
    {
        "name": "drama-ds-service",
        "port": 8010,
        "service_type": "ws",
        "protocols": ["websocket"],
        "metadata": {
            "service": "drama-ds",
            "version": "1.0.0"
        },
        "cluster": "DEFAULT",
        "group": "DEFAULT_GROUP"
    }
]

class NacosConfig:
    """Nacos配置管理类"""
    
    def __init__(self):
        self.config = {
            "server_addresses": "localhost:8848",
            "namespace": "",
            "username": None,
            "password": None,
            "services": DEFAULT_SERVICES
        }
    
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        self.config.update({
            "server_addresses": os.environ.get('NACOS_ADDRESS', self.config['server_addresses']),
            "namespace": os.environ.get('NACOS_NAMESPACE', self.config['namespace']),
            "username": os.environ.get('NACOS_USERNAME', self.config['username']),
            "password": os.environ.get('NACOS_PASSWORD', self.config['password'])
        })
        logger.info("已从环境变量加载Nacos配置")
        
        # 打印当前配置信息
        logger.info(f"Nacos服务器地址: {self.config['server_addresses']}")
        logger.info(f"Nacos命名空间: {self.config['namespace']}")
        logger.info(f"Nacos认证信息: {'已配置' if self.config['username'] else '未配置'}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
    
    def get_server_addresses(self) -> str:
        """获取Nacos服务器地址"""
        return self.config.get('server_addresses', 'localhost:8848')
    
    def get_namespace(self) -> str:
        """获取命名空间"""
        return self.config.get('namespace', '')
    
    def get_username(self) -> Optional[str]:
        """获取用户名"""
        return self.config.get('username')
    
    def get_password(self) -> Optional[str]:
        """获取密码"""
        return self.config.get('password')
    
    def get_services(self) -> List[Dict[str, Any]]:
        """获取服务配置列表"""
        return self.config.get('services', [])


# 全局配置实例
_config = NacosConfig()

def get_config() -> NacosConfig:
    """获取全局配置实例"""
    global _config
    return _config

def load_config() -> bool:
    """
    加载配置
    
    Returns:
        是否加载成功
    """
    global _config
    
    # 从环境变量加载
    _config.load_from_env()
    return True 