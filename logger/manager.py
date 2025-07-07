"""
日志管理器核心实现

支持多种输出方式，自动集成 TraceID，
基于上下文的结构化日志记录。

性能优化特性：
- 异步日志处理，避免阻塞主线程
- 批量发送，减少网络请求次数
- 队列缓冲，处理高并发场景
- 失败重试机制
"""

import logging
import logging.handlers
import sys
import threading
import queue
import time
import json
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from ..context.manager import get_current_context, Context

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


class AsyncTLSHandler(logging.Handler):
    """高性能异步火山引擎 TLS 日志处理器
    
    特性：
    - 异步处理，不阻塞主线程
    - 批量发送，减少网络请求
    - 队列缓冲，处理高并发
    - 自动重试机制
    - 优雅关闭
    """
    
    def __init__(self, config: Dict[str, Any], topic_id: str = None, service_name: str = None):
        super().__init__()
        self.config = config
        self.topic_id = topic_id or config.get("topic_id", "")
        self.service_name = service_name or config.get("service_name", "")
        self.client = None
        
        # 性能配置
        self.batch_size = config.get("batch_size", 100)  # 批量发送大小
        self.batch_timeout = config.get("batch_timeout", 5.0)  # 批量超时时间(秒)
        self.queue_size = config.get("queue_size", 10000)  # 队列大小
        self.worker_threads = config.get("worker_threads", 2)  # 工作线程数
        self.retry_times = config.get("retry_times", 3)  # 重试次数
        self.retry_delay = config.get("retry_delay", 1.0)  # 重试延迟(秒)
        
        # 内部状态
        self.log_queue = queue.Queue(maxsize=self.queue_size)
        self.executor = ThreadPoolExecutor(max_workers=self.worker_threads, thread_name_prefix="tls-logger")
        self.shutdown_event = threading.Event()
        self.batch_buffer = []
        self.last_batch_time = time.time()
        
        # 初始化客户端和启动工作线程
        self._init_client()
        self._start_workers()
    
    def _init_client(self):
        """初始化 TLS 客户端"""
        try:
            tls_config = self._parse_tls_config()
            
            if not tls_config or not tls_config.get("endpoint"):
                logging.getLogger("py_sdk.logger").info("TLS 配置为空或无效，跳过初始化")
                return
            
            try:
                from volcengine.tls.TLSService import TLSService
            except ImportError as e:
                logging.getLogger("py_sdk.logger").warning(
                    f"火山引擎 TLS SDK 未安装，TLS 日志功能不可用: {str(e)}. "
                    f"请安装: pip install volcengine"
                )
                return
            
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
            
            token = tls_config.get("token", "")
            if token:
                self.client.set_session_token(token)
            
            logging.getLogger("py_sdk.logger").info("异步TLS客户端初始化成功")
            
        except Exception as e:
            logging.getLogger("py_sdk.logger").error(f"异步TLS客户端初始化失败: {str(e)}")
            self.client = None
    
    def _parse_tls_config(self) -> Dict[str, str]:
        """解析 TLS 配置"""
        if "endpoint" in self.config:
            return {
                "endpoint": self.config.get("endpoint", ""),
                "access_key_id": self.config.get("access_key_id", ""),
                "access_key_secret": self.config.get("access_key_secret", ""),
                "region": self.config.get("region", "cn-beijing"),
                "token": self.config.get("token", "")
            }
        
        try:
            from py_sdk.nacos_sdk.api import get_config
            import json
            
            tls_config = get_config("tls.log.config")
            if tls_config:
                config_data = json.loads(tls_config)
                
                if "VOLCENGINE_ENDPOINT" in config_data:
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
            
            volcengine_config = get_config("volcengine.json")
            if volcengine_config:
                config_data = json.loads(volcengine_config)
                
                if "VOLCENGINE_ENDPOINT" in config_data:
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
                else:
                    return {
                        "endpoint": config_data.get("endpoint", ""),
                        "access_key_id": config_data.get("access_key_id", ""),
                        "access_key_secret": config_data.get("access_key_secret", ""),
                        "region": config_data.get("region", "cn-beijing"),
                        "token": config_data.get("token", "")
                    }
            
        except Exception as e:
            logging.getLogger("py_sdk.logger").debug(f"从 Nacos 获取火山引擎配置失败: {str(e)}")
        
        return {}
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(self.worker_threads):
            self.executor.submit(self._worker_loop, f"worker-{i}")
    
    def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        logging.getLogger("py_sdk.logger").debug(f"TLS日志工作线程 {worker_name} 启动")
        
        while not self.shutdown_event.is_set():
            try:
                # 尝试获取日志记录
                try:
                    record = self.log_queue.get(timeout=1.0)
                    if record is None:  # 关闭信号
                        break
                    
                    self.batch_buffer.append(record)
                    
                    # 检查是否需要发送批量
                    current_time = time.time()
                    should_send = (
                        len(self.batch_buffer) >= self.batch_size or
                        (self.batch_buffer and current_time - self.last_batch_time >= self.batch_timeout)
                    )
                    
                    if should_send:
                        self._send_batch()
                        self.last_batch_time = current_time
                    
                except queue.Empty:
                    # 超时检查是否需要发送剩余日志
                    current_time = time.time()
                    if self.batch_buffer and current_time - self.last_batch_time >= self.batch_timeout:
                        self._send_batch()
                        self.last_batch_time = current_time
                    continue
                
            except Exception as e:
                logging.getLogger("py_sdk.logger").error(f"TLS工作线程 {worker_name} 异常: {str(e)}")
                time.sleep(1.0)
        
        # 发送剩余的日志
        if self.batch_buffer:
            self._send_batch()
        
        logging.getLogger("py_sdk.logger").debug(f"TLS日志工作线程 {worker_name} 停止")
    
    def _send_batch(self):
        """批量发送日志"""
        if not self.client or not self.topic_id or not self.batch_buffer:
            self.batch_buffer.clear()
            return
        
        batch_to_send = self.batch_buffer.copy()
        self.batch_buffer.clear()
        
        for attempt in range(self.retry_times):
            try:
                # 构建批量日志
                log_contents = []
                for record in batch_to_send:
                    log_content = {
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                        "trace_id": getattr(record, 'trace_id', 'unknown'),
                        "service_name": self.service_name or "unknown",
                        "module": record.module,
                        "function": record.funcName,
                        "line": str(record.lineno),
                        "thread": str(record.thread),
                        "process": str(record.process),
                        "timestamp": int(record.created)
                    }
                    
                    if record.exc_info:
                        log_content["exception"] = self.format(record)
                    
                    if hasattr(record, 'extra') and record.extra:
                        log_content.update(record.extra)
                    
                    log_contents.append(log_content)
                
                # 发送到TLS
                try:
                    from volcengine.tls.tls_requests import PutLogsV2Request, PutLogsV2Logs
                except ImportError:
                    logging.getLogger("py_sdk.logger").error("无法导入 TLS 请求类")
                    return
                
                logs = PutLogsV2Logs(source=self.service_name or "python-sdk", filename="application.log")
                
                for log_content in log_contents:
                    timestamp = log_content.pop("timestamp")
                    logs.add_log(contents=log_content, log_time=timestamp)
                
                request = PutLogsV2Request(self.topic_id, logs)
                response = self.client.put_logs_v2(request)
                
                # 成功发送
                logging.getLogger("py_sdk.logger").debug(f"批量发送 {len(batch_to_send)} 条日志成功")
                return
                
            except Exception as e:
                if attempt < self.retry_times - 1:
                    logging.getLogger("py_sdk.logger").warning(
                        f"TLS批量发送失败 (尝试 {attempt + 1}/{self.retry_times}): {str(e)}"
                    )
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                else:
                    logging.getLogger("py_sdk.logger").error(
                        f"TLS批量发送最终失败，丢弃 {len(batch_to_send)} 条日志: {str(e)}"
                    )
    
    def emit(self, record):
        """异步发送日志记录"""
        if not self.client or not self.topic_id:
            return
        
        try:
            # 非阻塞方式添加到队列
            self.log_queue.put_nowait(record)
        except queue.Full:
            # 队列满了，丢弃日志并记录警告
            logging.getLogger("py_sdk.logger").warning("TLS日志队列已满，丢弃日志记录")
    
    def close(self):
        """关闭处理器"""
        logging.getLogger("py_sdk.logger").info("正在关闭异步TLS日志处理器...")
        
        # 发送关闭信号
        self.shutdown_event.set()
        
        # 向队列发送关闭信号
        for _ in range(self.worker_threads):
            try:
                self.log_queue.put_nowait(None)
            except queue.Full:
                pass
        
        # 等待工作线程完成，使用超时避免无限等待
        try:
            import threading
            import time
            
            # 先尝试优雅关闭，不等待
            self.executor.shutdown(wait=False)
            
            # 等待最多2秒让线程自然结束
            time.sleep(2.0)
                
        except Exception as e:
            logging.getLogger("py_sdk.logger").warning(f"关闭TLS工作线程时出现异常: {e}")
        
        logging.getLogger("py_sdk.logger").info("异步TLS日志处理器已关闭")
        super().close()


# 保持原有的TLSHandler作为备选（重命名为SyncTLSHandler）
class SyncTLSHandler(logging.Handler):
    """同步火山引擎 TLS 日志处理器（原版本）"""
    
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
            tls_config = self._parse_tls_config()
            
            if not tls_config or not tls_config.get("endpoint"):
                logging.getLogger("py_sdk.logger").info("TLS 配置为空或无效，跳过初始化")
                return
            
            try:
                from volcengine.tls.TLSService import TLSService
            except ImportError as e:
                logging.getLogger("py_sdk.logger").warning(
                    f"火山引擎 TLS SDK 未安装，TLS 日志功能不可用: {str(e)}. "
                    f"请安装: pip install volcengine"
                )
                return
            
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
            
            token = tls_config.get("token", "")
            if token:
                self.client.set_session_token(token)
            
            logging.getLogger("py_sdk.logger").info("同步TLS客户端初始化成功")
            
        except Exception as e:
            logging.getLogger("py_sdk.logger").error(f"同步TLS客户端初始化失败: {str(e)}")
            self.client = None
    
    def _parse_tls_config(self) -> Dict[str, str]:
        """解析 TLS 配置，支持多种格式"""
        if "endpoint" in self.config:
            return {
                "endpoint": self.config.get("endpoint", ""),
                "access_key_id": self.config.get("access_key_id", ""),
                "access_key_secret": self.config.get("access_key_secret", ""),
                "region": self.config.get("region", "cn-beijing"),
                "token": self.config.get("token", "")
            }
        
        try:
            from py_sdk.nacos_sdk.api import get_config
            import json
            
            tls_config = get_config("tls.log.config")
            if tls_config:
                config_data = json.loads(tls_config)
                
                if "VOLCENGINE_ENDPOINT" in config_data:
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
            
            volcengine_config = get_config("volcengine.json")
            if volcengine_config:
                config_data = json.loads(volcengine_config)
                
                if "VOLCENGINE_ENDPOINT" in config_data:
                    return {
                        "endpoint": config_data.get("VOLCENGINE_ENDPOINT", ""),
                        "access_key_id": config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                        "access_key_secret": config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                        "region": config_data.get("VOLCENGINE_REGION", "cn-beijing"),
                        "token": config_data.get("VOLCENGINE_TOKEN", "")
                    }
                else:
                    return {
                        "endpoint": config_data.get("endpoint", ""),
                        "access_key_id": config_data.get("access_key_id", ""),
                        "access_key_secret": config_data.get("access_key_secret", ""),
                        "region": config_data.get("region", "cn-beijing"),
                        "token": config_data.get("token", "")
                    }
            
        except Exception as e:
            logging.getLogger("py_sdk.logger").info(f"从 Nacos 获取火山引擎配置失败: {str(e)}")
        
        return {}

    def emit(self, record):
        """发送日志到 TLS"""
        if not self.client or not self.topic_id:
            return
        
        try:
            trace_id = getattr(record, 'trace_id', 'unknown')
            
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
            
            if record.exc_info:
                log_content["exception"] = self.format(record)
            
            if hasattr(record, 'extra') and record.extra:
                log_content.update(record.extra)
            
            timestamp = int(record.created)
            
            try:
                from volcengine.tls.tls_requests import PutLogsV2Request, PutLogsV2Logs
            except ImportError:
                print("无法导入 TLS 请求类，请确认 volcengine 包已正确安装", file=sys.stderr)
                return
            
            logs = PutLogsV2Logs(source=self.service_name or "python-sdk", filename="application.log")
            logs.add_log(contents=log_content, log_time=timestamp)
            
            request = PutLogsV2Request(self.topic_id, logs)
            
            try:
                response = self.client.put_logs_v2(request)
            except Exception as api_error:
                print(f"TLS API 调用失败: {str(api_error)}", file=sys.stderr)
            
        except Exception as e:
            print(f"TLS 日志发送失败: {str(e)}", file=sys.stderr)


# 为了向后兼容，保持TLSHandler指向异步版本
TLSHandler = AsyncTLSHandler


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
        logging.getLogger("py_sdk.logger").info("日志管理器初始化完成")
    
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
            from py_sdk.nacos_sdk.api import get_config
            import json
            
            # 首先尝试从 tls.log.config 获取配置
            tls_log_config = get_config("tls.log.config")
            config_data = None
            
            if tls_log_config:
                config_data = json.loads(tls_log_config)
                logging.getLogger("py_sdk.logger").info("从 Nacos tls.log.config 加载火山引擎配置")
            else:
                # 备用：尝试从 volcengine.json 获取配置（保持向后兼容）
                volcengine_config = get_config("volcengine.json")
                if volcengine_config:
                    config_data = json.loads(volcengine_config)
                    logging.getLogger("py_sdk.logger").info("从 Nacos volcengine.json 加载火山引擎配置（兼容模式）")
            
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
                
                logging.getLogger("py_sdk.logger").info("火山引擎 TLS 配置加载完成")
                        
        except Exception as e:
            # 只在 TLS 处理器启用时才记录警告
            if self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
                logging.getLogger("py_sdk.logger").warning(
                    f"加载火山引擎配置失败: {str(e)}"
                )
            else:
                logging.getLogger("py_sdk.logger").debug(
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
            
            # 检查是否使用同步模式
            use_sync = tls_config.get("sync_mode", False)
            
            if use_sync:
                # 使用同步处理器（原版本）
                tls_handler = SyncTLSHandler(
                    config=tls_config,
                    topic_id=self.topic_id or tls_config.get("topic_id"),
                    service_name=self.service_name or tls_config.get("service_name")
                )
                logging.getLogger("py_sdk.logger").info("使用同步TLS日志处理器")
            else:
                # 使用异步处理器（默认）
                tls_handler = AsyncTLSHandler(
                    config=tls_config,
                    topic_id=self.topic_id or tls_config.get("topic_id"),
                    service_name=self.service_name or tls_config.get("service_name")
                )
                logging.getLogger("py_sdk.logger").info("使用异步TLS日志处理器")
            
            tls_handler.setLevel(getattr(logging, tls_config.get("level", "INFO").upper()))
            tls_handler.setFormatter(formatter)
            root_logger.addHandler(tls_handler)
            
            # 保存TLS处理器引用，用于关闭时清理
            self.tls_handler = tls_handler
    
    def close(self):
        """关闭日志管理器"""
        logging.getLogger("py_sdk.logger").info("正在关闭日志管理器...")
        
        # 关闭TLS处理器
        if hasattr(self, 'tls_handler') and self.tls_handler:
            self.tls_handler.close()
        
        # 关闭其他处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        logging.getLogger("py_sdk.logger").info("日志管理器已关闭")
    
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
    
    Note:
        强制重新初始化以确保TLS配置正确应用
    """
    global _logger_manager
    
    # 强制重新初始化，确保TLS配置正确应用
    if _logger_manager is not None:
        logging.getLogger("py_sdk.logger").info("强制重新初始化日志管理器以应用新配置")
        # 简单地重置为None，让垃圾回收处理旧的管理器
        _logger_manager = None
    
    # 创建新的日志管理器
    _logger_manager = LoggerManager(topic_id=topic_id, service_name=service_name)
    _logger_manager.init_from_config(config)


def is_logger_initialized() -> bool:
    """
    检查日志管理器是否已经初始化
    
    Returns:
        bool: 如果已初始化返回True，否则返回False
    """
    global _logger_manager
    return _logger_manager is not None and _logger_manager.initialized


def get_logger_manager() -> LoggerManager:
    """获取全局日志管理器"""
    global _logger_manager
    if _logger_manager is None:
        # 如果没有初始化，使用默认配置初始化
        _logger_manager = LoggerManager()
        _logger_manager.init_from_config({})
        logging.getLogger("py_sdk.logger").info("使用默认配置初始化日志管理器")
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