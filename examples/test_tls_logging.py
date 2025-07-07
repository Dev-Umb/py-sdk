#!/usr/bin/env python3
"""
TLS 日志功能测试脚本

用于测试火山引擎 TLS 日志服务的集成是否正常工作。
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context.manager import create_context
from logger.manager import init_logger_manager, get_logger


def test_tls_logging():
    """测试 TLS 日志功能"""
    print("开始测试 TLS 日志功能...")
    
    # 配置日志管理器
    config = {
        "level": "DEBUG",
        "handlers": {
            "console": {
                "enabled": True,
                "level": "DEBUG"
            },
            "tls": {
                "enabled": True,
                "level": "INFO"
            }
        }
    }
    
    # 使用你的实际 TopicID
    topic_id = "2a6a07f0-8490-4a72-9a41-e5f25c578751"
    service_name = "py_sdk-test"
    
    # 初始化日志管理器
    init_logger_manager(config, topic_id=topic_id, service_name=service_name)
    
    # 获取日志记录器
    logger = get_logger("test.tls")
    
    # 创建测试上下文
    ctx = create_context()
    
    print(f"使用 TraceID: {ctx.trace_id}")
    print(f"使用 TopicID: {topic_id}")
    print(f"使用 ServiceName: {service_name}")
    
    # 发送测试日志
    logger.info(ctx, "TLS 日志测试开始", test_type="integration", component="tls")
    logger.debug(ctx, "这是一条调试日志", debug_info="详细调试信息")
    logger.warning(ctx, "这是一条警告日志", warning_type="test")
    logger.error(ctx, "这是一条错误日志", error_code="TEST_001")
    
    # 测试异常日志
    try:
        raise ValueError("这是一个测试异常")
    except Exception:
        logger.exception(ctx, "捕获到测试异常", exception_type="ValueError")
    
    logger.info(ctx, "TLS 日志测试完成", test_result="success")
    
    print("日志发送完成，请检查火山引擎 TLS 控制台查看日志是否正常接收")
    print("如果没有看到日志，请检查：")
    print("1. Nacos 配置 tls.log.config 是否正确")
    print("2. TopicID 是否有效")
    print("3. 火山引擎认证信息是否正确")
    print("4. 网络连接是否正常")


if __name__ == "__main__":
    test_tls_logging() 