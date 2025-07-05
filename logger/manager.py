"""
日志管理器核心实现

支持多种输出方式，自动集成 TraceID，
基于上下文的结构化日志记录。
"""

import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from context.manager import get_current_context, Context

# 默认配置
DEFAULT_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s",
    "handlers": {
        "console": {
            "enabled": True,
            "level": "INFO"
        },
        "file": {
            "enabled": False,
            "level": "INFO",
            "filename": "app.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "tls": {
            "enabled": False,
            "endpoint": "",
            "project": "",
            "logstore": "",
            "access_key_id": "",
            "access_key_secret": ""
        }
    }
}


class TraceIDFormatter(logging.Formatter):
    """支持 TraceID 的日志格式化器"""
    
    def format(self, record):
        # 获取当前上下文中的 TraceID
        context = get_current_context()
        trace_id = context.trace_id if context else "unknown"
        
        # 添加 trace_id 到日志记录
        record.trace_id = trace_id
        

        
        return super().format(record)


class TLSHandler(logging.Handler):
    """火山引擎 TLS 日志处理器"""
    
    def __init__(self, config: Dict[str, Any], topic_id: str = None, service_name: str = None):
        super().__init__()
        self.config = config
        self.topic_id = topic_id or config.get("topic_id", "")
        self.service_name = service_name or config.get("service_name", "")
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 TLS 客户端"""
        try:
            # 首先检查是否有必要的配置
            tls_config = self._parse_tls_config()
            
            if not tls_config or not tls_config.get("endpoint"):
                logging.getLogger("py-sdk.logger").info("TLS 配置为空或无效，跳过初始化")
                return
            
            # 尝试导入火山引擎 TLS SDK
            try:
                # 正确的导入方式
                from volcengine.tls.TLSService import TLSService
            except ImportError as e:
                logging.getLogger("py-sdk.logger").warning(
                    f"火山引擎 TLS SDK 未安装，TLS 日志功能不可用: {str(e)}. "
                    f"请安装: pip install volcengine"
                )
                return
            
            # 初始化 TLS 服务
            region = tls_config.get("region", "cn-beijing")
            endpoint = tls_config.get("endpoint", "")
            if not endpoint:
                endpoint = f"https://tls-{region}.volces.com"
            
            self.client = TLSService(
                endpoint=endpoint,
                access_key_id=tls_config.get("access_key_id", ""),
                access_key_secret=tls_config.get("access_key_secret", ""),
                region=region
            )
            
            # 如果有 token，设置 token
            token = tls_config.get("token", "")
            if token:
                self.client.set_session_token(token)
            
            logging.getLogger("py-sdk.logger").info("TLS 客户端初始化成功")
            
        except Exception as e:
            logging.getLogger("py-sdk.logger").error(
                f"TLS 客户端初始化失败: {str(e)}"
            )
            # 确保客户端为 None，避免后续使用
            self.client = None
    
    def _parse_tls_config(self) -> Dict[str, str]:
        """解析 TLS 配置，支持多种格式"""
        # 如果配置中直接包含 TLS 配置
        if "endpoint" in self.config:
            return {
                "endpoint": self.config.get("endpoint", ""),
                "access_key_id": self.config.get("access_key_id", ""),
                "access_key_secret": self.config.get("access_key_secret", ""),
                "region": self.config.get("region", "cn-beijing"),
                "token": self.config.get("token", "")
            }
        
        # 尝试从 Nacos 获取火山引擎配置（使用新的 dataID）
        try:
            from nacos_sdk.api import get_config
            import json
            
            # 首先尝试从 tls.log.config 获取配置
            tls_config = get_config("tls.log.config")
            if tls_config:
                config_data = json.loads(tls_config)
                
                # 支持 VOLCENGINE_ 前缀格式
                if "VOLCENGINE_ENDPOINT" in config_data:
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
            
            # 备用：尝试从 volcengine.json 获取配置（保持向后兼容）
            volcengine_config = get_config("volcengine.json")
            if volcengine_config:
                config_data = json.loads(volcengine_config)
                
                # 支持两种配置格式
                if "VOLCENGINE_ENDPOINT" in config_data:
                    # 新格式：VOLCENGINE_ 前缀
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
                else:
                    # 旧格式：直接字段名
                    return {
                        "endpoint": config_data.get("endpoint", ""),
                        "access_key_id": config_data.get("access_key_id", ""),
                        "access_key_secret": config_data.get("access_key_secret", ""),
                        "region": config_data.get("region", "cn-beijing"),
                        "token": config_data.get("token", "")
                    }
            
        except Exception as e:
            logging.getLogger("py-sdk.logger").info(
                f"从 Nacos 获取火山引擎配置失败: {str(e)}"
            )
        
        # 返回空配置
        return {}
    
    def emit(self, record):
        """发送日志到 TLS"""
        if not self.client or not self.topic_id:
            return
        
        try:
            # 获取 trace_id
            trace_id = getattr(record, 'trace_id', 'unknown')
            
            # 构建日志内容（按照火山引擎TLS要求的格式）
            log_content = {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "trace_id": trace_id,
                "service_name": self.service_name or "unknown",
                "module": record.module,
                "function": record.funcName,
                "line": str(record.lineno),
                "thread": str(record.thread),
                "process": str(record.process)
            }
            
            # 添加异常信息（如果有）
            if record.exc_info:
                log_content["exception"] = self.format(record)
            
            # 添加额外的字段（如果有）
            if hasattr(record, 'extra') and record.extra:
                log_content.update(record.extra)
            
            # 使用当前时间戳（秒）
            timestamp = int(record.created)
            
            # 导入必要的类
            try:
                from volcengine.tls.tls_requests import PutLogsV2Request, PutLogsV2Logs
            except ImportError:
                print("无法导入 TLS 请求类，请确认 volcengine 包已正确安装", file=sys.stderr)
                return
            
            # 构建 PutLogsV2Logs 对象
            logs = PutLogsV2Logs(source=self.service_name or "python-sdk", filename="application.log")
            
            # 添加日志项
            logs.add_log(contents=log_content, log_time=timestamp)
            
            # 构建 PutLogsV2Request
            request = PutLogsV2Request(self.topic_id, logs)
            
            # 调用 TLS API
            try:
                response = self.client.put_logs_v2(request)
                # 检查响应（put_logs_v2 通常返回 None 或简单对象）
                # 如果没有异常，说明发送成功
            except Exception as api_error:
                print(f"TLS API 调用失败: {str(api_error)}", file=sys.stderr)
            
        except Exception as e:
            # 避免日志处理器自身的错误影响应用
            print(f"TLS 日志发送失败: {str(e)}", file=sys.stderr)


class SDKLogger:
    """SDK 日志记录器"""
    
    def __init__(self, name: str, logger: logging.Logger):
        self.name = name
        self.logger = logger
    
    def _log(self, level: int, context: Optional[Context], message: str, **kwargs):
        """内部日志记录方法"""
        # 如果没有传入上下文，尝试获取当前上下文
        if context is None:
            context = get_current_context()
        
        # 构建额外信息
        extra = {}
        if context:
            extra['trace_id'] = context.trace_id
        
        # 分离 logging 参数和 extra 参数
        log_kwargs = {}
        extra_kwargs = {}
        
        # logging 保留的参数
        log_params = {'exc_info', 'stack_info', 'stacklevel'}
        
        for key, value in kwargs.items():
            if key in log_params:
                log_kwargs[key] = value
            else:
                extra_kwargs[key] = value
        
        # 添加用户传入的额外信息
        extra.update(extra_kwargs)
        
        # 记录日志
        self.logger.log(level, message, extra=extra, **log_kwargs)
    
    def debug(self, context: Optional[Context], message: str, **kwargs):
        """记录 DEBUG 级别日志"""
        self._log(logging.DEBUG, context, message, **kwargs)
    
    def info(self, context: Optional[Context], message: str, **kwargs):
        """记录 INFO 级别日志"""
        self._log(logging.INFO, context, message, **kwargs)
    
    def warning(self, context: Optional[Context], message: str, **kwargs):
        """记录 WARNING 级别日志"""
        self._log(logging.WARNING, context, message, **kwargs)
    
    def error(self, context: Optional[Context], message: str, **kwargs):
        """记录 ERROR 级别日志"""
        self._log(logging.ERROR, context, message, **kwargs)
    
    def critical(self, context: Optional[Context], message: str, **kwargs):
        """记录 CRITICAL 级别日志"""
        self._log(logging.CRITICAL, context, message, **kwargs)
    
    def exception(self, context: Optional[Context], message: str, **kwargs):
        """记录异常日志"""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, context, message, **kwargs)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, topic_id: str = None, service_name: str = None):
        self.config = DEFAULT_CONFIG.copy()
        self.loggers = {}
        self.initialized = False
        self.topic_id = topic_id
        self.service_name = service_name
    
    def init_from_config(self, config: Dict[str, Any]):
        """从配置初始化日志管理器"""
        if self.initialized:
            return
        
        # 合并配置
        self._merge_config(config)
        
        # 自动加载火山引擎配置
        self._load_volcengine_config()
        
        # 设置根日志级别
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config["level"].upper()))
        
        # 配置处理器
        self._setup_handlers()
        
        self.initialized = True
        logging.getLogger("py-sdk.logger").info("日志管理器初始化完成")
    
    def _merge_config(self, config: Dict[str, Any]):
        """合并配置"""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, config)
    
    def _load_volcengine_config(self):
        """加载火山引擎配置"""
        try:
            from nacos_sdk.api import get_config
            import json
            
            # 首先尝试从 tls.log.config 获取配置
            tls_log_config = get_config("tls.log.config")
            config_data = None
            
            if tls_log_config:
                config_data = json.loads(tls_log_config)
                logging.getLogger("py-sdk.logger").info("从 Nacos tls.log.config 加载火山引擎配置")
            else:
                # 备用：尝试从 volcengine.json 获取配置（保持向后兼容）
                volcengine_config = get_config("volcengine.json")
                if volcengine_config:
                    config_data = json.loads(volcengine_config)
                    logging.getLogger("py-sdk.logger").info("从 Nacos volcengine.json 加载火山引擎配置（兼容模式）")
            
            # 如果获取到配置且TLS处理器已启用，自动配置火山引擎参数
            if config_data and self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
                tls_config = self.config["handlers"]["tls"]
                
                # 支持 VOLCENGINE_ 前缀格式
                if "VOLCENGINE_ENDPOINT" in config_data:
                    tls_config.update({
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    })
                
                # 支持旧格式（直接字段名）
                elif "endpoint" in config_data:
                    tls_config.update({
                        "endpoint": config_data.get("endpoint", ""),
                        "access_key_id": config_data.get("access_key_id", ""),
                        "access_key_secret": config_data.get("access_key_secret", ""),
                        "region": config_data.get("region", "cn-beijing"),
                        "token": config_data.get("token", "")
                    })
                
                # 设置 TopicID 和 ServiceName（如果在初始化时提供了）
                if self.topic_id:
                    tls_config["topic_id"] = self.topic_id
                
                if self.service_name:
                    tls_config["service_name"] = self.service_name
                
                logging.getLogger("py-sdk.logger").info("火山引擎 TLS 配置加载完成")
                        
        except Exception as e:
            # 只在 TLS 处理器启用时才记录警告
            if self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
                logging.getLogger("py-sdk.logger").warning(
                    f"加载火山引擎配置失败: {str(e)}"
                )
            else:
                logging.getLogger("py-sdk.logger").debug(
                    f"跳过火山引擎配置加载: {str(e)}"
                )
    
    def _setup_handlers(self):
        """设置日志处理器"""
        root_logger = logging.getLogger()
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = TraceIDFormatter(self.config["format"])
        
        # 控制台处理器
        if self.config["handlers"]["console"]["enabled"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(
                getattr(logging, self.config["handlers"]["console"]["level"].upper())
            )
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # 文件处理器
        if self.config["handlers"]["file"]["enabled"]:
            file_config = self.config["handlers"]["file"]
            file_handler = logging.handlers.RotatingFileHandler(
                filename=file_config["filename"],
                maxBytes=file_config["max_bytes"],
                backupCount=file_config["backup_count"],
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, file_config["level"].upper()))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # TLS 处理器
        if self.config["handlers"]["tls"]["enabled"]:
            tls_config = self.config["handlers"]["tls"]
            tls_handler = TLSHandler(
                config=tls_config,
                topic_id=self.topic_id or tls_config.get("topic_id"),
                service_name=self.service_name or tls_config.get("service_name")
            )
            tls_handler.setLevel(getattr(logging, tls_config.get("level", "INFO").upper()))
            tls_handler.setFormatter(formatter)
            root_logger.addHandler(tls_handler)
    
    def get_logger(self, name: str) -> SDKLogger:
        """获取日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = SDKLogger(name, logger)
        
        return self.loggers[name]


# 全局日志管理器实例
_logger_manager: Optional[LoggerManager] = None


def init_logger_manager(config: Dict[str, Any], topic_id: str = None, service_name: str = None):
    """
    初始化全局日志管理器
    
    Args:
        config: 日志配置字典
        topic_id: 火山引擎 TLS TopicID（必需，每个服务不同）
        service_name: 服务名称（可选，用于日志标识）
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager(topic_id=topic_id, service_name=service_name)
    
    _logger_manager.init_from_config(config)


def get_logger_manager() -> LoggerManager:
    """获取全局日志管理器"""
    if _logger_manager is None:
        init_logger_manager({})
    return _logger_manager


def get_logger(name: str) -> SDKLogger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        SDK 日志记录器实例
        
    Example:
        >>> from py_sdk.logger import get_logger
        >>> from py_sdk.context import create_context
        >>> 
        >>> logger = get_logger(__name__)
        >>> ctx = create_context()
        >>> logger.info(ctx, "这是一条日志")
    """
    manager = get_logger_manager()
    return manager.get_logger(name) 