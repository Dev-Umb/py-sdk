"""
HTTP 业务状态码定义

定义所有业务相关的状态码，与传统 HTTP 状态码分离。
HTTP 响应始终为 200，但 body 中包含具体的业务状态码。

状态码规则：
- 0: 成功
- 10001~19999: 系统级错误
- 20001~29999: 认证授权错误
- 30001~39999: 参数验证错误
- 40001~49999: 业务逻辑错误
- 50001~59999: 第三方服务错误
- 60001~69999: 数据库相关错误
- 70001~79999: 缓存相关错误
- 80001~89999: 消息队列相关错误
- 90001~99999: 其他错误
"""

from typing import Optional


class BusinessCode:
    """业务状态码类"""
    
    def __init__(self, code: int, message: str, i18n: str = ""):
        """
        初始化业务状态码
        
        Args:
            code: 状态码
            message: 错误信息
            i18n: 国际化键值（可选）
        """
        self.code = code
        self.message = message
        self.i18n = i18n
    
    def __str__(self) -> str:
        return f"BusinessCode(code={self.code}, message='{self.message}')"
    
    def __repr__(self) -> str:
        return self.__str__()


# ============================================================================
# 成功状态码
# ============================================================================

# 通用成功
OK = BusinessCode(0, "OK")

# ============================================================================
# 系统级错误 (10001~19999)
# ============================================================================

# 服务器错误
INTERNAL_SERVER_ERROR = BusinessCode(10001, "Internal server error")
SERVICE_UNAVAILABLE = BusinessCode(10002, "Service unavailable")
REQUEST_TIMEOUT = BusinessCode(10003, "Request timeout")
RATE_LIMIT_EXCEEDED = BusinessCode(10004, "Rate limit exceeded")

# 请求处理错误
BODY_BIND_ERROR = BusinessCode(10101, "Body bind error")
JSON_PARSE_ERROR = BusinessCode(10102, "JSON parse error")
REQUEST_TOO_LARGE = BusinessCode(10103, "Request entity too large")
UNSUPPORTED_MEDIA_TYPE = BusinessCode(10104, "Unsupported media type")

# 配置相关错误
CONFIG_ERROR = BusinessCode(10201, "Configuration error")
DATABASE_CONFIG_ERROR = BusinessCode(10202, "Database configuration error")
REDIS_CONFIG_ERROR = BusinessCode(10203, "Redis configuration error")

# ============================================================================
# 认证授权错误 (20001~29999)
# ============================================================================

# 认证错误
UNAUTHORIZED = BusinessCode(20001, "Unauthorized")
TOKEN_INVALID = BusinessCode(20002, "Token is invalid")
TOKEN_EXPIRED = BusinessCode(20003, "Token has expired")
TOKEN_MISSING = BusinessCode(20004, "Token is missing")

# 授权错误
FORBIDDEN = BusinessCode(20101, "Forbidden")
INSUFFICIENT_PERMISSIONS = BusinessCode(20102, "Insufficient permissions")
ACCESS_DENIED = BusinessCode(20103, "Access denied")

# 用户状态错误
USER_NOT_FOUND = BusinessCode(20201, "User not found")
USER_DISABLED = BusinessCode(20202, "User is disabled")
USER_LOCKED = BusinessCode(20203, "User account is locked")

# ============================================================================
# 参数验证错误 (30001~39999)
# ============================================================================

# 通用参数错误
INVALID_PARAMS = BusinessCode(30001, "Invalid parameters")
MISSING_REQUIRED_PARAM = BusinessCode(30002, "Missing required parameter")
PARAM_TYPE_ERROR = BusinessCode(30003, "Parameter type error")
PARAM_OUT_OF_RANGE = BusinessCode(30004, "Parameter out of range")

# 格式验证错误
INVALID_EMAIL_FORMAT = BusinessCode(30101, "Invalid email format")
INVALID_PHONE_FORMAT = BusinessCode(30102, "Invalid phone number format")
INVALID_DATE_FORMAT = BusinessCode(30103, "Invalid date format")
INVALID_URL_FORMAT = BusinessCode(30104, "Invalid URL format")

# 长度验证错误
PARAM_TOO_SHORT = BusinessCode(30201, "Parameter too short")
PARAM_TOO_LONG = BusinessCode(30202, "Parameter too long")

# ============================================================================
# 业务逻辑错误 (40001~49999)
# ============================================================================

# 资源不存在
RESOURCE_NOT_FOUND = BusinessCode(40001, "Resource not found")
ROOM_NOT_FOUND = BusinessCode(40002, "房间不存在")
ORDER_NOT_FOUND = BusinessCode(40003, "订单不存在")
PRODUCT_NOT_FOUND = BusinessCode(40004, "商品不存在")

# 资源状态错误
RESOURCE_ALREADY_EXISTS = BusinessCode(40101, "Resource already exists")
RESOURCE_LOCKED = BusinessCode(40102, "Resource is locked")
RESOURCE_EXPIRED = BusinessCode(40103, "Resource has expired")

# 业务规则错误
INSUFFICIENT_BALANCE = BusinessCode(40201, "余额不足")
QUOTA_EXCEEDED = BusinessCode(40202, "配额已超限")
OPERATION_NOT_ALLOWED = BusinessCode(40203, "操作不被允许")
DUPLICATE_OPERATION = BusinessCode(40204, "重复操作")

# 房间相关错误
ROOM_FULL = BusinessCode(40301, "房间已满")
ROOM_CLOSED = BusinessCode(40302, "房间已关闭")
ROOM_PERMISSION_DENIED = BusinessCode(40303, "房间权限不足")

# 订单相关错误
ORDER_ALREADY_PAID = BusinessCode(40401, "订单已支付")
ORDER_CANCELLED = BusinessCode(40402, "订单已取消")
ORDER_EXPIRED = BusinessCode(40403, "订单已过期")

# ============================================================================
# 第三方服务错误 (50001~59999)
# ============================================================================

# 支付服务错误
PAYMENT_SERVICE_ERROR = BusinessCode(50001, "Payment service error")
PAYMENT_FAILED = BusinessCode(50002, "Payment failed")
REFUND_FAILED = BusinessCode(50003, "Refund failed")

# 短信服务错误
SMS_SERVICE_ERROR = BusinessCode(50101, "SMS service error")
SMS_SEND_FAILED = BusinessCode(50102, "SMS send failed")
SMS_CODE_EXPIRED = BusinessCode(50103, "SMS verification code expired")

# 邮件服务错误
EMAIL_SERVICE_ERROR = BusinessCode(50201, "Email service error")
EMAIL_SEND_FAILED = BusinessCode(50202, "Email send failed")

# 文件存储服务错误
STORAGE_SERVICE_ERROR = BusinessCode(50301, "Storage service error")
FILE_UPLOAD_FAILED = BusinessCode(50302, "File upload failed")
FILE_NOT_FOUND = BusinessCode(50303, "File not found")

# ============================================================================
# 数据库相关错误 (60001~69999)
# ============================================================================

# 数据库连接错误
DATABASE_CONNECTION_ERROR = BusinessCode(60001, "Database connection error")
DATABASE_TIMEOUT = BusinessCode(60002, "Database operation timeout")

# 数据操作错误
DATA_NOT_FOUND = BusinessCode(60101, "Data not found")
DATA_ALREADY_EXISTS = BusinessCode(60102, "Data already exists")
DATA_CONSTRAINT_VIOLATION = BusinessCode(60103, "Data constraint violation")
DATA_INTEGRITY_ERROR = BusinessCode(60104, "Data integrity error")

# 事务错误
TRANSACTION_FAILED = BusinessCode(60201, "Transaction failed")
DEADLOCK_DETECTED = BusinessCode(60202, "Database deadlock detected")

# ============================================================================
# 缓存相关错误 (70001~79999)
# ============================================================================

# Redis 错误
REDIS_CONNECTION_ERROR = BusinessCode(70001, "Redis connection error")
REDIS_TIMEOUT = BusinessCode(70002, "Redis operation timeout")
CACHE_MISS = BusinessCode(70003, "Cache miss")

# ============================================================================
# 消息队列相关错误 (80001~89999)
# ============================================================================

# 消息队列错误
MQ_CONNECTION_ERROR = BusinessCode(80001, "Message queue connection error")
MQ_SEND_FAILED = BusinessCode(80002, "Message send failed")
MQ_CONSUME_FAILED = BusinessCode(80003, "Message consume failed")

# ============================================================================
# 其他错误 (90001~99999)
# ============================================================================

# 网络相关错误
NETWORK_ERROR = BusinessCode(90001, "Network error")
CONNECTION_REFUSED = BusinessCode(90002, "Connection refused")
DNS_RESOLUTION_FAILED = BusinessCode(90003, "DNS resolution failed")

# 限流相关错误
TOO_MANY_REQUESTS = BusinessCode(90101, "Too many requests")
CONCURRENT_LIMIT_EXCEEDED = BusinessCode(90102, "Concurrent limit exceeded")

# 维护相关错误
SYSTEM_MAINTENANCE = BusinessCode(90201, "System under maintenance")
FEATURE_DISABLED = BusinessCode(90202, "Feature is disabled")


# ============================================================================
# 工具函数
# ============================================================================

def get_code_by_value(code_value: int) -> Optional[BusinessCode]:
    """
    根据状态码值获取对应的 BusinessCode 对象
    
    Args:
        code_value: 状态码值
        
    Returns:
        对应的 BusinessCode 对象，如果不存在则返回 None
    """
    # 获取当前模块中所有的 BusinessCode 对象
    import sys
    current_module = sys.modules[__name__]
    
    for attr_name in dir(current_module):
        attr_value = getattr(current_module, attr_name)
        if isinstance(attr_value, BusinessCode) and attr_value.code == code_value:
            return attr_value
    
    return None


def is_success_code(code: BusinessCode) -> bool:
    """
    判断是否为成功状态码
    
    Args:
        code: 业务状态码
        
    Returns:
        是否为成功状态码
    """
    return code.code == 0


def is_error_code(code: BusinessCode) -> bool:
    """
    判断是否为错误状态码
    
    Args:
        code: 业务状态码
        
    Returns:
        是否为错误状态码
    """
    return code.code != 0


def get_error_category(code: BusinessCode) -> str:
    """
    获取错误类别
    
    Args:
        code: 业务状态码
        
    Returns:
        错误类别描述
    """
    if code.code == 0:
        return "success"
    elif 10001 <= code.code <= 19999:
        return "system_error"
    elif 20001 <= code.code <= 29999:
        return "auth_error"
    elif 30001 <= code.code <= 39999:
        return "param_error"
    elif 40001 <= code.code <= 49999:
        return "business_error"
    elif 50001 <= code.code <= 59999:
        return "third_party_error"
    elif 60001 <= code.code <= 69999:
        return "database_error"
    elif 70001 <= code.code <= 79999:
        return "cache_error"
    elif 80001 <= code.code <= 89999:
        return "mq_error"
    elif 90001 <= code.code <= 99999:
        return "other_error"
    else:
        return "unknown_error" 