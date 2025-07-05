class NacosException(Exception):
    """Nacos相关异常基类"""
    def __init__(self, message: str, code: int = 0):
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")
        
class NacosConnectionException(NacosException):
    """Nacos连接异常"""
    def __init__(self, message: str):
        super().__init__(message, 1)
        
class NacosAuthException(NacosException):
    """Nacos认证异常"""
    def __init__(self, message: str):
        super().__init__(message, 2)
        
class NacosRegisterException(NacosException):
    """Nacos注册异常"""
    def __init__(self, message: str):
        super().__init__(message, 3)
        
class NacosDeregisterException(NacosException):
    """Nacos注销异常"""
    def __init__(self, message: str):
        super().__init__(message, 4) 