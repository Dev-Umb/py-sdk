import logging
import random
from typing import Dict, Any, List, Optional, Tuple, Callable, Union

from nacos.client import get_nacos_client
from nacos.exceptions import NacosException

logger = logging.getLogger("nacos-discovery")

def get_service_instances(service_name: str, group_name: str = "DEFAULT_GROUP",
                         clusters: str = None, healthy_only: bool = True) -> List[Dict[str, Any]]:
    """
    获取指定服务的所有实例列表
    
    Args:
        service_name: 服务名称
        group_name: 分组名称，默认为DEFAULT_GROUP
        clusters: 集群名称，多个集群用逗号分隔，如 "DEFAULT,CLUSTER-A"
        healthy_only: 是否只返回健康实例，默认为True
    
    Returns:
        实例列表
    """
    client = get_nacos_client()
    if client is None:
        return []
    
    return client.get_service_instances(
        service_name=service_name,
        group_name=group_name,
        clusters=clusters,
        healthy_only=healthy_only
    )

def get_one_instance(service_name: str, group_name: str = "DEFAULT_GROUP",
                    clusters: str = None, healthy_only: bool = True,
                    strategy: str = "random") -> Optional[Dict[str, Any]]:
    """
    获取指定服务的一个实例，可以指定负载均衡策略
    
    Args:
        service_name: 服务名称
        group_name: 分组名称，默认为DEFAULT_GROUP
        clusters: 集群名称，多个集群用逗号分隔，如 "DEFAULT,CLUSTER-A"
        healthy_only: 是否只返回健康实例，默认为True
        strategy: 负载均衡策略，可选值：random(随机), weight(权重), 默认为random
    
    Returns:
        实例信息，如果没有可用实例则返回None
    """
    instances = get_service_instances(service_name, group_name, clusters, healthy_only)
    
    if not instances:
        logger.warning(f"No available instances found for service: {service_name}")
        return None
    
    if strategy == "weight":
        # 按权重选择实例
        total_weight = sum(instance.get("weight", 1.0) for instance in instances)
        if total_weight <= 0:
            return random.choice(instances)
        
        # 生成一个0到总权重之间的随机数
        rand_weight = random.uniform(0, total_weight)
        curr_weight = 0
        for instance in instances:
            curr_weight += instance.get("weight", 1.0)
            if curr_weight >= rand_weight:
                return instance
        
        return instances[-1]  # 不应该到达这里，但以防万一
    else:
        # 默认使用随机策略
        return random.choice(instances)

def get_service_url(service_name: str, group_name: str = "DEFAULT_GROUP",
                   clusters: str = None, healthy_only: bool = True,
                   strategy: str = "random", 
                   protocol: str = "http",
                   path: str = "") -> Optional[str]:
    """
    获取服务URL
    
    Args:
        service_name: 服务名称
        group_name: 分组名称，默认为DEFAULT_GROUP
        clusters: 集群名称，多个集群用逗号分隔，如 "DEFAULT,CLUSTER-A"
        healthy_only: 是否只返回健康实例，默认为True
        strategy: 负载均衡策略，可选值：random(随机), weight(权重)，默认为random
        protocol: 协议，默认为http
        path: 路径，默认为空字符串
    
    Returns:
        服务URL，如果没有可用实例则返回None
    """
    instance = get_one_instance(service_name, group_name, clusters, healthy_only, strategy)
    
    if not instance:
        return None
    
    ip = instance.get("ip")
    port = instance.get("port")
    
    if not ip or not port:
        logger.warning(f"Invalid instance data: {instance}")
        return None
    
    # 格式化路径，确保以/开头
    if path and not path.startswith("/"):
        path = f"/{path}"
    
    return f"{protocol}://{ip}:{port}{path}"

def get_ws_url(service_name: str, group_name: str = "DEFAULT_GROUP",
              clusters: str = None, healthy_only: bool = True,
              strategy: str = "random", 
              path: str = "ws", 
              secure: bool = False) -> Optional[str]:
    """
    获取WebSocket服务URL
    
    Args:
        service_name: 服务名称
        group_name: 分组名称，默认为DEFAULT_GROUP
        clusters: 集群名称，多个集群用逗号分隔，如 "DEFAULT,CLUSTER-A"
        healthy_only: 是否只返回健康实例，默认为True
        strategy: 负载均衡策略，可选值：random(随机), weight(权重)，默认为random
        path: WebSocket路径，默认为"ws"
        secure: 是否使用安全的WebSocket连接(wss)，默认为False
    
    Returns:
        WebSocket服务URL，如果没有可用实例则返回None
    """
    protocol = "wss" if secure else "ws"
    
    return get_service_url(
        service_name=service_name,
        group_name=group_name,
        clusters=clusters,
        healthy_only=healthy_only,
        strategy=strategy,
        protocol=protocol,
        path=path
    ) 