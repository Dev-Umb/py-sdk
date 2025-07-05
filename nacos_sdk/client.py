import json
import time
import socket
import logging
import asyncio
import os
from typing import Dict, Any, Optional, List, Union
import requests

from .exceptions import NacosException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nacos-client")

class NacosClient:
    def __init__(self, server_addresses: str = None, namespace: str = "", username: str = None, password: str = None):
        """
        初始化Nacos客户端
        
        Args:
            server_addresses: Nacos服务器地址，格式为 "ip1:port1,ip2:port2"
                             如果为None，将从环境变量NACOS_SERVER_ADDRESSES读取
                             如果环境变量也没有，则使用默认地址 "127.0.0.1:8848"
            namespace: 命名空间ID，可从环境变量NACOS_NAMESPACE读取
            username: 用户名，如果启用了认证，可从环境变量NACOS_USERNAME读取
            password: 密码，如果启用了认证，可从环境变量NACOS_PASSWORD读取
        """
        # 优先级：参数 > 环境变量 > 默认值
        self.server_addresses = self._get_server_addresses(server_addresses)
        self.namespace = namespace or os.getenv('NACOS_NAMESPACE', '')
        self.username = username or os.getenv('NACOS_USERNAME')
        self.password = password or os.getenv('NACOS_PASSWORD')
        self.beat_tasks = {}  # 用于存储心跳任务
        self.auth_token = None
        self.token_ttl = 0
        
        logger.info(f"Initialized Nacos client with servers: {','.join(self.server_addresses)}")
        if self.namespace:
            logger.info(f"Using namespace: {self.namespace}")
        
        if self.username and self.password:
            self._login()
    
    def _get_server_addresses(self, server_addresses: str = None) -> List[str]:
        """
        获取Nacos服务器地址列表
        
        Args:
            server_addresses: 直接传入的服务器地址
            
        Returns:
            服务器地址列表
        """
        if server_addresses:
            # 优先使用传入的参数
            addresses = server_addresses.split(',')
        else:
            # 从环境变量读取
            env_addresses = os.getenv('NACOS_SERVER_ADDRESSES')
            if env_addresses:
                addresses = env_addresses.split(',')
            else:
                # 使用默认地址
                addresses = ['127.0.0.1:8848']
                logger.info("No server addresses provided, using default: 127.0.0.1:8848")
        
        # 清理地址格式
        cleaned_addresses = []
        for addr in addresses:
            addr = addr.strip()
            if addr:
                cleaned_addresses.append(addr)
        
        return cleaned_addresses
    
    def _login(self):
        """登录Nacos获取认证令牌"""
        try:
            url = f"http://{self.server_addresses[0]}/nacos/v1/auth/login"
            params = {
                "username": self.username,
                "password": self.password
            }
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("accessToken")
                self.token_ttl = data.get("tokenTtl", 18000) - 10  # 提前10秒刷新token
                logger.info("Successfully logged in to Nacos")
            else:
                logger.error(f"Failed to login to Nacos: {response.text}")
        except Exception as e:
            logger.error(f"Login to Nacos failed: {str(e)}")
    
    def _build_request_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """构建请求参数，包含认证信息"""
        if self.auth_token:
            params["accessToken"] = self.auth_token
        return params
    
    def register_service(self, service_name: str, ip: str, port: int, 
                          cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP", 
                          metadata: Dict[str, str] = None, ephemeral: bool = True,
                          weight: float = 1.0, enabled: bool = True) -> bool:
        """
        注册服务实例到Nacos
        
        Args:
            service_name: 服务名称
            ip: 服务IP地址
            port: 服务端口
            cluster_name: 集群名称，默认为DEFAULT
            group_name: 分组名称，默认为DEFAULT_GROUP
            metadata: 服务元数据，可以包含任意键值对
            ephemeral: 是否是临时实例，临时实例需要心跳
            weight: 权重，影响负载均衡，默认为1.0
            enabled: 是否启用，默认为True
            
        Returns:
            注册是否成功
        """
        try:
            url = f"http://{self.server_addresses[0]}/nacos/v1/ns/instance"
            metadata_str = json.dumps(metadata) if metadata else "{}"
            
            params = {
                "serviceName": service_name,
                "ip": ip,
                "port": port,
                "clusterName": cluster_name,
                "groupName": group_name,
                "metadata": metadata_str,
                "ephemeral": str(ephemeral).lower(),
                "weight": weight,
                "enabled": str(enabled).lower(),
                "namespaceId": self.namespace
            }
            
            params = self._build_request_params(params)
            response = requests.post(url, params=params)
            
            if response.status_code == 200 and response.text.upper() == "OK":
                logger.info(f"Successfully registered service: {service_name}:{ip}:{port}")
                
                # 如果是临时实例，启动心跳任务
                if ephemeral:
                    instance_id = f"{ip}#{port}#{cluster_name}#{service_name}"
                    self.start_beat_task(service_name, ip, port, cluster_name, group_name, metadata)
                
                return True
            else:
                logger.error(f"Failed to register service: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Register service failed: {str(e)}")
            return False
    
    def deregister_service(self, service_name: str, ip: str, port: int, 
                           cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP") -> bool:
        """
        注销服务实例
        
        Args:
            service_name: 服务名称
            ip: 服务IP地址
            port: 服务端口
            cluster_name: 集群名称，默认为DEFAULT
            group_name: 分组名称，默认为DEFAULT_GROUP
            
        Returns:
            注销是否成功
        """
        try:
            url = f"http://{self.server_addresses[0]}/nacos/v1/ns/instance"
            
            params = {
                "serviceName": service_name,
                "ip": ip,
                "port": port,
                "clusterName": cluster_name,
                "groupName": group_name,
                "namespaceId": self.namespace
            }
            
            params = self._build_request_params(params)
            response = requests.delete(url, params=params)
            
            if response.status_code == 200 and response.text.upper() == "OK":
                logger.info(f"Successfully deregistered service: {service_name}:{ip}:{port}")
                
                # 停止心跳任务
                instance_id = f"{ip}#{port}#{cluster_name}#{service_name}"
                self.stop_beat_task(instance_id)
                
                return True
            else:
                logger.error(f"Failed to deregister service: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Deregister service failed: {str(e)}")
            return False
    
    async def send_beat(self, service_name: str, ip: str, port: int, 
                        cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP",
                        metadata: Dict[str, str] = None):
        """
        发送心跳
        
        Args:
            service_name: 服务名称
            ip: 服务IP地址
            port: 服务端口
            cluster_name: 集群名称，默认为DEFAULT
            group_name: 分组名称，默认为DEFAULT_GROUP
            metadata: 服务元数据
        """
        try:
            url = f"http://{self.server_addresses[0]}/nacos/v1/ns/instance/beat"
            
            beat_info = {
                "ip": ip,
                "port": port,
                "serviceName": service_name,
                "cluster": cluster_name,
                "metadata": metadata or {}
            }
            
            params = {
                "serviceName": service_name,
                "groupName": group_name,
                "ephemeral": "true",
                "beat": json.dumps(beat_info),
                "namespaceId": self.namespace
            }
            
            params = self._build_request_params(params)
            response = requests.put(url, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to send beat: {response.text}")
        except Exception as e:
            logger.warning(f"Send beat failed: {str(e)}")
    
    async def beat_task(self, service_name: str, ip: str, port: int, 
                        cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP",
                        metadata: Dict[str, str] = None):
        """
        心跳任务，每5秒发送一次心跳
        """
        while True:
            try:
                await self.send_beat(service_name, ip, port, cluster_name, group_name, metadata)
                await asyncio.sleep(5)  # 5秒发送一次心跳
            except asyncio.CancelledError:
                logger.info(f"Beat task for {service_name}:{ip}:{port} cancelled")
                break
            except Exception as e:
                logger.error(f"Beat task error: {str(e)}")
                await asyncio.sleep(5)
    
    def start_beat_task(self, service_name: str, ip: str, port: int, 
                        cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP",
                        metadata: Dict[str, str] = None):
        """
        启动心跳任务
        """
        instance_id = f"{ip}#{port}#{cluster_name}#{service_name}"
        
        # 如果已存在，先停止
        self.stop_beat_task(instance_id)
        
        # 创建新的心跳任务
        task = asyncio.create_task(
            self.beat_task(service_name, ip, port, cluster_name, group_name, metadata)
        )
        self.beat_tasks[instance_id] = task
        logger.info(f"Started beat task for {service_name}:{ip}:{port}")
    
    def stop_beat_task(self, instance_id: str):
        """
        停止心跳任务
        """
        task = self.beat_tasks.pop(instance_id, None)
        if task:
            task.cancel()
            logger.info(f"Stopped beat task for {instance_id}")
    
    def get_service_instances(self, service_name: str, group_name: str = "DEFAULT_GROUP",
                              clusters: str = None, healthy_only: bool = True) -> List[Dict[str, Any]]:
        """
        获取服务实例列表
        
        Args:
            service_name: 服务名称
            group_name: 分组名称，默认为DEFAULT_GROUP
            clusters: 集群名称，多个集群用逗号分隔，如 "DEFAULT,CLUSTER-A"
            healthy_only: 是否只返回健康实例
            
        Returns:
            实例列表
        """
        try:
            url = f"http://{self.server_addresses[0]}/nacos/v1/ns/instance/list"
            
            params = {
                "serviceName": service_name,
                "groupName": group_name,
                "namespaceId": self.namespace,
                "healthyOnly": str(healthy_only).lower()
            }
            
            if clusters:
                params["clusters"] = clusters
                
            params = self._build_request_params(params)
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                hosts = result.get("hosts", [])
                logger.info(f"Found {len(hosts)} instances for {service_name}")
                return hosts
            else:
                logger.error(f"Failed to get service instances: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Get service instances failed: {str(e)}")
            return []


# 用于全局共享的客户端实例
_nacos_client = None

def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def init_nacos_client(server_addresses: str = None, namespace: str = "", 
                      username: str = None, password: str = None) -> NacosClient:
    """
    初始化Nacos客户端
    
    Args:
        server_addresses: Nacos服务器地址，格式为 "ip1:port1,ip2:port2"
                         如果为None，将从环境变量NACOS_SERVER_ADDRESSES读取
                         如果环境变量也没有，则使用默认地址 "127.0.0.1:8848"
        namespace: 命名空间ID，可从环境变量NACOS_NAMESPACE读取
        username: 用户名，如果启用了认证，可从环境变量NACOS_USERNAME读取
        password: 密码，如果启用了认证，可从环境变量NACOS_PASSWORD读取
    
    Returns:
        NacosClient实例
    """
    global _nacos_client
    if _nacos_client is None:
        _nacos_client = NacosClient(server_addresses, namespace, username, password)
    return _nacos_client

def get_nacos_client() -> Optional[NacosClient]:
    """获取已初始化的Nacos客户端实例"""
    global _nacos_client
    if _nacos_client is None:
        logger.warning("Nacos client is not initialized. Please call init_nacos_client first.")
    return _nacos_client

def registerNacos(service_name: str, port: int, 
                  server_addresses: str = None, namespace: str = "",
                  username: str = None, password: str = None,
                  metadata: Dict[str, str] = None, 
                  cluster_name: str = "DEFAULT", group_name: str = "DEFAULT_GROUP",
                  ip: str = None) -> bool:
    """
    注册服务到Nacos
    
    Args:
        service_name: 服务名称
        port: 服务端口
        server_addresses: Nacos服务器地址，格式为 "ip1:port1,ip2:port2"
                         如果为None，将从环境变量NACOS_SERVER_ADDRESSES读取
                         如果环境变量也没有，则使用默认地址 "127.0.0.1:8848"
        namespace: 命名空间ID，可从环境变量NACOS_NAMESPACE读取
        username: 用户名，如果启用了认证，可从环境变量NACOS_USERNAME读取
        password: 密码，如果启用了认证，可从环境变量NACOS_PASSWORD读取
        metadata: 服务元数据，包含任意键值对
        cluster_name: 集群名称，默认为DEFAULT
        group_name: 分组名称，默认为DEFAULT_GROUP
        ip: 服务IP地址，如果为None则自动获取本机IP
    
    Returns:
        注册是否成功
    """
    # 初始化Nacos客户端
    client = init_nacos_client(server_addresses, namespace, username, password)
    
    # 如果未指定IP，获取本机IP
    if ip is None:
        ip = get_local_ip()
    
    # 注册服务
    return client.register_service(
        service_name=service_name,
        ip=ip,
        port=port,
        cluster_name=cluster_name,
        group_name=group_name,
        metadata=metadata or {},
        ephemeral=True  # 使用临时实例，需要心跳保活
    )


def unregisterNacos(service_name: str, port: int, 
                    ip: str = None, 
                    cluster_name: str = "DEFAULT", 
                    group_name: str = "DEFAULT_GROUP") -> bool:
    """
    从Nacos注销服务
    
    Args:
        service_name: 服务名称
        port: 服务端口
        ip: 服务IP地址，如果为None则自动获取本机IP
        cluster_name: 集群名称，默认为DEFAULT
        group_name: 分组名称，默认为DEFAULT_GROUP
    
    Returns:
        注销是否成功
    """
    # 获取已初始化的Nacos客户端
    client = get_nacos_client()
    if client is None:
        return False
    
    # 如果未指定IP，获取本机IP
    if ip is None:
        ip = get_local_ip()
    
    # 注销服务
    return client.deregister_service(
        service_name=service_name,
        ip=ip,
        port=port,
        cluster_name=cluster_name,
        group_name=group_name
    ) 