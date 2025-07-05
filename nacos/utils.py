import socket
import logging
import platform
import subprocess
from typing import Dict, List, Optional

logger = logging.getLogger("nacos-utils")

def get_local_ip() -> str:
    """
    获取本机IP地址
    
    Returns:
        本机IP地址，如果获取失败则返回"127.0.0.1"
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def is_port_available(port: int, host: str = '0.0.0.0') -> bool:
    """
    检查端口是否可用
    
    Args:
        port: 端口号
        host: 主机地址，默认为'0.0.0.0'
    
    Returns:
        端口是否可用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except Exception:
        return False

def find_available_port(start_port: int = 8000, end_port: int = 9000) -> Optional[int]:
    """
    查找可用端口
    
    Args:
        start_port: 起始端口号，默认为8000
        end_port: 结束端口号，默认为9000
    
    Returns:
        可用端口，如果没有可用端口则返回None
    """
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    return None

def get_service_metadata(service_type: str = "ws", 
                         protocols: List[str] = None, 
                         extra: Dict[str, str] = None) -> Dict[str, str]:
    """
    获取服务元数据
    
    Args:
        service_type: 服务类型，默认为"ws"
        protocols: 协议列表，默认为None
        extra: 额外的元数据，默认为None
    
    Returns:
        服务元数据
    """
    metadata = {
        "serviceType": service_type,
        "os": platform.system(),
        "version": platform.version(),
        "hostname": socket.gethostname()
    }
    
    if protocols:
        metadata["protocols"] = ",".join(protocols)
    
    if extra:
        metadata.update(extra)
    
    return metadata

def get_container_id() -> Optional[str]:
    """
    获取容器ID
    
    Returns:
        容器ID，如果不在容器中则返回None
    """
    try:
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                if 'docker' in line:
                    return line.split('/')[-1].strip()
        return None
    except Exception:
        return None

def get_pod_info() -> Dict[str, str]:
    """
    获取Kubernetes Pod信息
    
    Returns:
        Pod信息，如果不在K8s环境中则返回空字典
    """
    info = {}
    try:
        # 获取Pod名称
        with open('/etc/hostname', 'r') as f:
            info['podName'] = f.read().strip()
        
        # 获取命名空间
        cmd = "cat /var/run/secrets/kubernetes.io/serviceaccount/namespace"
        namespace = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        info['namespace'] = namespace
        
        return info
    except Exception:
        return {} 