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
    - 防御性保护，避免被意外清除
    """
    
    def __init__(self, config: Dict[str, Any], topic_id: str = None, service_name: str = None):
        super().__init__()
        self.config = config
        self.topic_id = topic_id or config.get("topic_id", "")
        self.service_name = service_name or config.get("service_name", "")
        self.client = None
        self._is_closing = False  # 防止重复关闭
        
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
        # 优先使用直接传入的配置
        if "endpoint" in self.config:
            return {
                "endpoint": self.config.get("endpoint", ""),
                "access_key_id": self.config.get("access_key_id", ""),
                "access_key_secret": self.config.get("access_key_secret", ""),
                "region": self.config.get("region", "cn-beijing"),
                "token": self.config.get("token", "")
            }
        
        # 如果没有直接配置，返回空字典，让LoggerManager处理Nacos配置加载
        logging.getLogger("py_sdk.logger").debug("使用LoggerManager预加载的TLS配置")
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
        if self._is_closing:
            return  # 防止重复关闭
        
        self._is_closing = True
        logging.getLogger("py_sdk.logger").info("正在关闭异步TLS日志处理器...")
        
        # 发送关闭信号
        self.shutdown_event.set()
        
        # 向队列发送关闭信号
        for _ in range(self.worker_threads):
            try:
                self.log_queue.put_nowait(None)
            except queue.Full:
                pass
        
        # 等待工作线程完成
        self.executor.shutdown(wait=True)
        
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
        # 优先使用直接传入的配置
        if "endpoint" in self.config:
            return {
                "endpoint": self.config.get("endpoint", ""),
                "access_key_id": self.config.get("access_key_id", ""),
                "access_key_secret": self.config.get("access_key_secret", ""),
                "region": self.config.get("region", "cn-beijing"),
                "token": self.config.get("token", "")
            }
        
        # 如果没有直接配置，返回空字典，让LoggerManager处理Nacos配置加载
        logging.getLogger("py_sdk.logger").debug("使用LoggerManager预加载的TLS配置")
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
    
    def debug(self, message: str, context: Optional[Context] = None, **kwargs):
        """记录 DEBUG 级别日志"""
        self._log(logging.DEBUG, context, message, **kwargs)
    
    def info(self, message: str, context: Optional[Context] = None, **kwargs):
        """记录 INFO 级别日志"""
        self._log(logging.INFO, context, message, **kwargs)
    
    def warning(self, message: str, context: Optional[Context] = None, **kwargs):
        """记录 WARNING 级别日志"""
        self._log(logging.WARNING, context, message, **kwargs)
    
    def error(self, message: str, context: Optional[Context] = None, **kwargs):
        """记录 ERROR 级别日志"""
        self._log(logging.ERROR, context, message, **kwargs)
    
    def critical(self, message: str, context: Optional[Context] = None, **kwargs):
        """记录 CRITICAL 级别日志"""
        self._log(logging.CRITICAL, context, message, **kwargs)
    
    def exception(self, message: str, context: Optional[Context] = None, **kwargs):
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
        # 只在 TLS 处理器启用时才加载配置
        if not self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
            logging.getLogger("py_sdk.logger").debug("TLS处理器未启用，跳过火山引擎配置加载")
            return
        
        tls_config = self.config["handlers"]["tls"]
        config_data = None
        
        try:
            from ..nacos_sdk.api import get_config
            import json
            
            # 首先尝试从 tls.log.config 获取配置
            tls_log_config = get_config("tls.log.config")
            
            if tls_log_config:
                config_data = json.loads(tls_log_config)
                logging.getLogger("py_sdk.logger").info("从 Nacos tls.log.config 加载火山引擎配置")
            else:
                # 备用：尝试从 volcengine.json 获取配置（保持向后兼容）
                volcengine_config = get_config("volcengine.json")
                if volcengine_config:
                    config_data = json.loads(volcengine_config)
                    logging.getLogger("py_sdk.logger").info("从 Nacos volcengine.json 加载火山引擎配置（兼容模式）")
            
            # 检查是否必须依赖Nacos配置
            if not config_data:
                error_msg = "无法从Nacos获取火山引擎TLS配置 (tls.log.config 或 volcengine.json)，TLS日志功能无法使用"
                logging.getLogger("py_sdk.logger").error(error_msg)
                raise Exception(error_msg)
            
            # 配置火山引擎参数
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
            else:
                error_msg = "Nacos配置中缺少火山引擎端点信息 (endpoint 或 VOLCENGINE_ENDPOINT)"
                logging.getLogger("py_sdk.logger").error(error_msg)
                raise Exception(error_msg)
            
            # 强制覆盖 TopicID 和 ServiceName（用户传入的配置优先）
            if self.topic_id:
                tls_config["topic_id"] = self.topic_id
                logging.getLogger("py_sdk.logger").info(f"使用用户指定的TopicID: {self.topic_id}")
            
            if self.service_name:
                tls_config["service_name"] = self.service_name
                logging.getLogger("py_sdk.logger").info(f"使用用户指定的ServiceName: {self.service_name}")
            
            # 验证必要的配置项
            required_fields = ["endpoint", "access_key_id", "access_key_secret"]
            missing_fields = [field for field in required_fields if not tls_config.get(field)]
            if missing_fields:
                error_msg = f"火山引擎TLS配置缺少必要字段: {missing_fields}"
                logging.getLogger("py_sdk.logger").error(error_msg)
                raise Exception(error_msg)
            
            if not tls_config.get("topic_id"):
                error_msg = "TopicID未设置，无法发送日志到火山引擎TLS"
                logging.getLogger("py_sdk.logger").error(error_msg)
                raise Exception(error_msg)
            
            logging.getLogger("py_sdk.logger").info("火山引擎 TLS 配置加载完成")
                        
        except Exception as e:
            logging.getLogger("py_sdk.logger").error(f"加载火山引擎配置失败: {str(e)}")
            # 禁用TLS处理器，避免后续错误
            self.config["handlers"]["tls"]["enabled"] = False
            raise e
    
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
    
    def _setup_tls_handler(self):
        """单独设置TLS处理器"""
        if not self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
            return
        
        root_logger = logging.getLogger()
        
        # 移除现有的TLS处理器
        for handler in root_logger.handlers[:]:
            if isinstance(handler, (AsyncTLSHandler, SyncTLSHandler)):
                handler.close()
                root_logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = TraceIDFormatter(self.config["format"])
        
        # 添加新的TLS处理器
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
    
    def _setup_tls_handler_force(self):
        """强制设置TLS处理器，即使已经存在也会重新创建"""
        if not self.config.get("handlers", {}).get("tls", {}).get("enabled", False):
            return
        
        root_logger = logging.getLogger()
        
        # 强制移除所有现有的TLS处理器
        handlers_to_remove = []
        for handler in root_logger.handlers:
            if isinstance(handler, (AsyncTLSHandler, SyncTLSHandler)):
                handlers_to_remove.append(handler)
        
        for handler in handlers_to_remove:
            try:
                handler.close()
            except:
                pass  # 忽略关闭错误
            root_logger.removeHandler(handler)
        # 创建格式化器
        formatter = TraceIDFormatter(self.config["format"])
        
        # 添加新的TLS处理器
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
            logging.getLogger("py_sdk.logger").info("强制使用同步TLS日志处理器")
        else:
            # 使用异步处理器（默认）
            tls_handler = AsyncTLSHandler(
                config=tls_config,
                topic_id=self.topic_id or tls_config.get("topic_id"),
                service_name=self.service_name or tls_config.get("service_name")
            )
            logging.getLogger("py_sdk.logger").info("强制使用异步TLS日志处理器")
        
        tls_handler.setLevel(getattr(logging, tls_config.get("level", "INFO").upper()))
        tls_handler.setFormatter(formatter)
        root_logger.addHandler(tls_handler)
        
        # 保存TLS处理器引用，用于关闭时清理
        self.tls_handler = tls_handler
        
        logging.getLogger("py_sdk.logger").info("TLS处理器强制重新添加完成")
    
    def get_logger(self, name: str) -> SDKLogger:
        """获取日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = SDKLogger(name, logger)
        
        return self.loggers[name]


# 全局日志管理器实例
_logger_manager: Optional[LoggerManager] = None

# 全局logger实例和name
_global_logger: Optional[SDKLogger] = None
_global_logger_name: Optional[str] = None


def init_logger_manager(config: Dict[str, Any], topic_id: str = None, service_name: str = None, logger_name: str = None):
    """
    初始化全局日志管理器，并设置全局logger name
    """
    global _logger_manager, _global_logger, _global_logger_name
    if _logger_manager is None:
        _logger_manager = LoggerManager(topic_id=topic_id, service_name=service_name)
        _logger_manager.init_from_config(config)
        if logger_name is None:
            logger_name = service_name
        _global_logger_name = logger_name or "py_sdk"
        _global_logger = _logger_manager.get_logger(_global_logger_name)
    else:
        # 如果已经初始化但提供了新的TLS配置，尝试重新配置TLS
        if config.get("handlers", {}).get("tls", {}).get("enabled", False) and (topic_id or service_name):
            logging.getLogger("py_sdk.logger").info("检测到TLS配置更新，强制重新配置TLS日志处理器")
            
            # 更新LoggerManager的topic_id和service_name
            if topic_id:
                _logger_manager.topic_id = topic_id
            if service_name:
                _logger_manager.service_name = service_name
            
            # 重新加载TLS配置
            try:
                _logger_manager._merge_config(config)
                _logger_manager._load_volcengine_config()
                
                # 强制重新设置TLS处理器，即使已经存在
                _logger_manager._setup_tls_handler_force()
                
                logging.getLogger("py_sdk.logger").info("TLS日志处理器强制重新配置完成")
            except Exception as e:
                logging.getLogger("py_sdk.logger").error(f"TLS日志处理器重新配置失败: {e}")
        else:
            logging.getLogger("py_sdk.logger").warning("日志管理器已经初始化，忽略重复初始化")


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


def get_logger() -> SDKLogger:
    """
    获取全局日志记录器，无需传name
    """
    global _global_logger
    if _global_logger is None:
        # 若未初始化，使用默认配置和默认name
        init_logger_manager({}, logger_name="py_sdk")
    return _global_logger 