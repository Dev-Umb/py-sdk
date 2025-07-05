import logging
import signal
import atexit
from typing import Dict, Any, List, Optional, Tuple, Callable

from nacos.client import registerNacos, unregisterNacos, get_local_ip
from nacos.config import get_config
from nacos.utils import get_service_metadata

logger = logging.getLogger("nacos-service")

class ServiceManager:
    """服务管理器，负责管理服务的注册和注销"""
    
    def __init__(self):
        self.registered_services = {}  # 保存已注册的服务信息
        self.initialized = False
        self.cleanup_registered = False
    
    def init(self) -> bool:
        """
        初始化服务管理器
        
        Returns:
            初始化是否成功
        """
        from nacos.config import load_config
        
        # 加载配置
        if not load_config():
            logger.error("加载Nacos配置失败")
            return False
        
        # 注册退出处理
        if not self.cleanup_registered:
            atexit.register(self.cleanup)
            self.register_signal_handlers()
            self.cleanup_registered = True
        
        self.initialized = True
        logger.info("服务管理器初始化成功")
        return True
    
    def register_signal_handlers(self):
        """注册信号处理函数"""
        def signal_handler(sig, frame):
            logger.info(f"接收到信号 {sig}，正在退出...")
            self.cleanup()
        
        # 注册 SIGINT 和 SIGTERM 信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def register_service(self, service_name: str, port: int, 
                       metadata: Dict[str, str] = None,
                       cluster_name: str = "DEFAULT", 
                       group_name: str = "DEFAULT_GROUP",
                       ip: str = None) -> bool:
        """
        注册服务
        
        Args:
            service_name: 服务名称
            port: 服务端口
            metadata: 服务元数据
            cluster_name: 集群名称
            group_name: 分组名称
            ip: 服务IP地址，默认为None，将自动获取
        
        Returns:
            注册是否成功
        """
        if not self.initialized:
            logger.warning("服务管理器未初始化，请先调用init方法")
            return False
        
        # 获取配置
        config = get_config()
        server_addresses = config.get_server_addresses()
        namespace = config.get_namespace()
        username = config.get_username()
        password = config.get_password()
        
        # 如果未指定IP，获取本机IP
        if ip is None:
            ip = get_local_ip()
        
        # 注册服务
        success = registerNacos(
            service_name=service_name,
            port=port,
            server_addresses=server_addresses,
            namespace=namespace,
            username=username,
            password=password,
            metadata=metadata or {},
            cluster_name=cluster_name,
            group_name=group_name,
            ip=ip
        )
        
        if success:
            # 保存注册信息，用于后续注销
            service_key = f"{service_name}:{port}"
            self.registered_services[service_key] = {
                "service_name": service_name,
                "port": port,
                "ip": ip,
                "cluster_name": cluster_name,
                "group_name": group_name
            }
            logger.info(f"服务 {service_name}:{port} 注册成功")
        else:
            logger.error(f"服务 {service_name}:{port} 注册失败")
        
        return success
    
    def unregister_service(self, service_name: str, port: int,
                          ip: str = None,
                          cluster_name: str = "DEFAULT", 
                          group_name: str = "DEFAULT_GROUP") -> bool:
        """
        注销服务
        
        Args:
            service_name: 服务名称
            port: 服务端口
            ip: 服务IP地址
            cluster_name: 集群名称
            group_name: 分组名称
        
        Returns:
            注销是否成功
        """
        service_key = f"{service_name}:{port}"
        
        # 如果有保存的注册信息，优先使用
        if service_key in self.registered_services:
            service_info = self.registered_services[service_key]
            result = unregisterNacos(
                service_name=service_info["service_name"],
                port=service_info["port"],
                ip=service_info["ip"],
                cluster_name=service_info["cluster_name"],
                group_name=service_info["group_name"]
            )
            
            if result:
                del self.registered_services[service_key]
                logger.info(f"服务 {service_name}:{port} 注销成功")
                return True
            else:
                logger.error(f"服务 {service_name}:{port} 注销失败")
                return False
        else:
            # 如果未指定IP，获取本机IP
            if ip is None:
                ip = get_local_ip()
            
            # 注销服务
            result = unregisterNacos(
                service_name=service_name,
                port=port,
                ip=ip,
                cluster_name=cluster_name,
                group_name=group_name
            )
            
            if result:
                logger.info(f"服务 {service_name}:{port} 注销成功")
            else:
                logger.error(f"服务 {service_name}:{port} 注销失败")
            
            return result
    
    def register_services_from_config(self) -> Tuple[int, int]:
        """
        从配置中注册服务
        
        Returns:
            成功注册的服务数量和总服务数量
        """
        if not self.initialized:
            logger.warning("服务管理器未初始化，请先调用init方法")
            return 0, 0
        
        config = get_config()
        services = config.get_services()
        
        if not services:
            logger.warning("配置中未找到服务定义")
            return 0, 0
        
        success_count = 0
        for service in services:
            service_name = service.get("name")
            port = service.get("port")
            
            if not service_name or not port:
                logger.warning(f"服务配置缺少必要参数: {service}")
                continue
            
            # 获取其他参数
            metadata = service.get("metadata", {})
            cluster_name = service.get("cluster", "DEFAULT")
            group_name = service.get("group", "DEFAULT_GROUP")
            ip = service.get("ip")
            
            # 如果指定了service_type，自动生成元数据
            if "service_type" in service:
                service_type = service["service_type"]
                protocols = service.get("protocols", [])
                extra_metadata = service.get("metadata", {})
                
                metadata = get_service_metadata(
                    service_type=service_type,
                    protocols=protocols,
                    extra=extra_metadata
                )
            
            # 注册服务
            if self.register_service(
                service_name=service_name,
                port=port,
                metadata=metadata,
                cluster_name=cluster_name,
                group_name=group_name,
                ip=ip
            ):
                success_count += 1
        
        logger.info(f"从配置成功注册 {success_count}/{len(services)} 个服务")
        return success_count, len(services)
    
    def cleanup(self):
        """清理所有已注册的服务"""
        logger.info("开始清理已注册的服务")
        
        for service_key, service_info in list(self.registered_services.items()):
            self.unregister_service(
                service_name=service_info["service_name"],
                port=service_info["port"],
                ip=service_info["ip"],
                cluster_name=service_info["cluster_name"],
                group_name=service_info["group_name"]
            )
        
        logger.info("服务清理完成")


# 全局服务管理器实例
_service_manager = ServiceManager()

def get_service_manager() -> ServiceManager:
    """获取全局服务管理器实例"""
    global _service_manager
    return _service_manager

def init_service_manager() -> bool:
    """
    初始化服务管理器
    
    Returns:
        初始化是否成功
    """
    global _service_manager
    return _service_manager.init()

def register_service(service_name: str, port: int, 
                   metadata: Dict[str, str] = None,
                   cluster_name: str = "DEFAULT", 
                   group_name: str = "DEFAULT_GROUP",
                   ip: str = None) -> bool:
    """
    注册服务
    
    Args:
        service_name: 服务名称
        port: 服务端口
        metadata: 服务元数据
        cluster_name: 集群名称
        group_name: 分组名称
        ip: 服务IP地址
        
    Returns:
        注册是否成功
    """
    global _service_manager
    return _service_manager.register_service(
        service_name=service_name,
        port=port,
        metadata=metadata,
        cluster_name=cluster_name,
        group_name=group_name,
        ip=ip
    )

def unregister_service(service_name: str, port: int,
                      ip: str = None,
                      cluster_name: str = "DEFAULT", 
                      group_name: str = "DEFAULT_GROUP") -> bool:
    """
    注销服务
    
    Args:
        service_name: 服务名称
        port: 服务端口
        ip: 服务IP地址
        cluster_name: 集群名称
        group_name: 分组名称
        
    Returns:
        注销是否成功
    """
    global _service_manager
    return _service_manager.unregister_service(
        service_name=service_name,
        port=port,
        ip=ip,
        cluster_name=cluster_name,
        group_name=group_name
    )

def register_services_from_config() -> Tuple[int, int]:
    """
    从配置中注册服务
    
    Returns:
        成功注册的服务数量和总服务数量
    """
    global _service_manager
    return _service_manager.register_services_from_config()

def cleanup():
    """清理所有已注册的服务"""
    global _service_manager
    _service_manager.cleanup() 