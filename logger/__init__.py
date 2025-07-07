"""
日志管理模块

提供统一的日志格式，自动包含 TraceID，
支持多种输出方式：控制台、文件、火山引擎 TLS。

使用方法：
1. 在应用启动时调用一次 init_logger() 或 init_logger_manager()
2. 在任何地方使用 get_logger(__name__) 获取logger实例
3. 使用 logger.info(context, message) 记录日志
"""

from .manager import (
    get_logger, 
    SDKLogger, 
    init_logger_manager, 
    get_logger_manager,
    is_logger_initialized
)

# 便捷的初始化函数
def init_logger(level="INFO", console=True, file=None, tls=None, topic_id=None, service_name=None, high_performance=True):
    """
    便捷的日志初始化函数
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: 是否启用控制台输出 (True/False)
        file: 文件输出配置 (None 或 文件路径字符串 或 配置字典)
        tls: TLS输出配置 (None 或 True 或 配置字典)
        topic_id: 火山引擎 TLS TopicID
        service_name: 服务名称
        high_performance: 是否启用高性能模式 (默认True，使用异步处理)
    
    Examples:
        # 最简单的初始化（只输出到控制台）
        init_logger()
        
        # 设置日志级别
        init_logger(level="DEBUG")
        
        # 启用文件输出
        init_logger(file="app.log")
        
        # 启用TLS输出（高性能模式）
        init_logger(tls=True, topic_id="your-topic-id")
        
        # 启用TLS输出（同步模式，兼容旧版本）
        init_logger(tls=True, topic_id="your-topic-id", high_performance=False)
        
        # 高性能TLS配置
        init_logger(
            level="INFO",
            console=True,
            tls={
                "batch_size": 200,      # 批量大小
                "batch_timeout": 3.0,   # 批量超时
                "queue_size": 20000,    # 队列大小
                "worker_threads": 4,    # 工作线程数
                "retry_times": 5        # 重试次数
            },
            topic_id="your-topic-id",
            service_name="your-service"
        )
    """
    config = {
        "level": level,
        "handlers": {
            "console": {
                "enabled": console,
                "level": level
            },
            "file": {
                "enabled": False
            },
            "tls": {
                "enabled": False
            }
        }
    }
    
    # 配置文件输出
    if file:
        config["handlers"]["file"]["enabled"] = True
        config["handlers"]["file"]["level"] = level
        
        if isinstance(file, str):
            config["handlers"]["file"]["filename"] = file
        elif isinstance(file, dict):
            config["handlers"]["file"].update(file)
    
    # 配置TLS输出
    if tls:
        config["handlers"]["tls"]["enabled"] = True
        config["handlers"]["tls"]["level"] = level
        
        # 设置性能模式
        if not high_performance:
            config["handlers"]["tls"]["sync_mode"] = True
        
        if isinstance(tls, dict):
            config["handlers"]["tls"].update(tls)
    
    init_logger_manager(config, topic_id=topic_id, service_name=service_name)

__all__ = [
    'get_logger',
    'SDKLogger',
    'init_logger_manager',
    'get_logger_manager',
    'init_logger',
    'is_logger_initialized'
] 