"""
火山引擎 TLS 日志使用示例

展示如何配置和使用火山引擎 TLS 日志功能，
包括从 Nacos 获取配置和传入 TopicID、ServiceName。
"""

from context.manager import create_context, set_context
from logger import init_logger_manager, get_logger


def demo_tls_logging_with_config():
    """演示使用配置文件的 TLS 日志"""
    print("=== TLS 日志配置示例 ===")
    
    # 日志配置（启用 TLS 处理器）
    logger_config = {
        "level": "INFO",
        "handlers": {
            "console": {
                "enabled": True,
                "level": "INFO"
            },
            "tls": {
                "enabled": True,
                "level": "INFO"
            }
        }
    }
    
    # 初始化日志管理器（传入 TopicID 和 ServiceName）
    init_logger_manager(
        config=logger_config,
        topic_id="",  # 每个服务的 TopicID 不同
        service_name="demo-service"     # 服务名称
    )
    
    # 创建上下文
    ctx = create_context()
    set_context(ctx)
    
    # 获取日志记录器
    logger = get_logger("tls-demo")
    
    print(f"TraceID: {ctx.trace_id}")
    print("开始记录日志...")
    
    # 记录各种级别的日志
    logger.info(ctx, "TLS 日志测试 - 信息级别")
    logger.warning(ctx, "TLS 日志测试 - 警告级别")
    logger.error(ctx, "TLS 日志测试 - 错误级别")
    
    # 记录带额外字段的日志
    logger.info(ctx, "用户操作", extra={
        "user_id": 12345,
        "action": "login",
        "ip_address": "192.168.1.100"
    })
    
    # 记录异常日志
    try:
        1 / 0
    except Exception:
        logger.exception(ctx, "发生异常")
    
    print("日志记录完成，已发送到火山引擎 TLS")


def demo_tls_logging_minimal():
    """演示最简化的 TLS 日志配置"""
    print("\n=== 最简化 TLS 日志示例 ===")
    
    # 最简配置（只启用 TLS，其他使用默认配置）
    minimal_config = {
        "handlers": {
            "tls": {
                "enabled": True
            }
        }
    }
    
    # 初始化（只传入必需的 TopicID）
    init_logger_manager(
        config=minimal_config,
        topic_id="your-topic-id-here"
    )
    
    ctx = create_context()
    logger = get_logger("minimal-demo")
    
    logger.info(ctx, "最简化配置的 TLS 日志测试")
    print("最简化配置完成")


def demo_nacos_config_format():
    """演示 Nacos 配置格式"""
    print("\n=== Nacos 配置格式说明 ===")
    
    nacos_config_example = {
        "dataID": "tls.log.config",
        "content": {
            "VOLCENGINE_ENDPOINT": "https://tls-cn-beijing.volces.com",
            "VOLCENGINE_ACCESS_KEY_ID": "AKLTNsaddmU5MWNjYjQ3YTVkNDEzOTg3ZjQ0ZWNmYWM0MzljODc",
            "VOLCENGINE_ACCESS_KEY_SECRET": "sdasdadas==",
            "VOLCENGINE_TOKEN": "",
            "VOLCENGINE_REGION": "cn-beijing"
        }
    }
    
    print("Nacos 配置示例：")
    print(f"DataID: {nacos_config_example['dataID']}")
    print("配置内容：")
    for key, value in nacos_config_example['content'].items():
        if 'SECRET' in key or 'KEY' in key:
            print(f"  {key}: {'*' * 20}  # 实际值已隐藏")
        else:
            print(f"  {key}: {value}")
    
    print("\n注意事项：")
    print("1. TopicID 和 ServiceName 需要在代码中传入，不在 Nacos 配置中")
    print("2. 每个服务的 TopicID 都不同，需要根据实际情况设置")
    print("3. 如果没有传入配置，将使用默认的 Nacos DataID 获取")


def demo_logger_api_usage():
    """演示日志 API 的各种用法"""
    print("\n=== 日志 API 使用示例 ===")
    
    # 简单配置
    config = {
        "handlers": {
            "console": {"enabled": True},
            "tls": {"enabled": True}
        }
    }
    
    init_logger_manager(
        config=config,
        topic_id="demo-topic-123",
        service_name="api-demo-service"
    )
    
    ctx = create_context()
    logger = get_logger("api-demo")
    
    # 1. 基础日志
    logger.info(ctx, "基础信息日志")
    
    # 2. 带参数的日志
    user_id = 12345
    action = "create_order"
    logger.info(ctx, f"用户 {user_id} 执行操作: {action}")
    
    # 3. 带额外字段的结构化日志
    logger.info(ctx, "订单创建", extra={
        "order_id": "ORD-2023-001",
        "amount": 99.99,
        "currency": "CNY",
        "payment_method": "alipay"
    })
    
    # 4. 错误日志
    logger.error(ctx, "订单处理失败", extra={
        "error_code": "PAYMENT_FAILED",
        "order_id": "ORD-2023-002"
    })
    
    # 5. 调试日志（需要设置日志级别为 DEBUG）
    logger.debug(ctx, "调试信息", extra={
        "debug_data": {"step": 1, "status": "processing"}
    })
    
    print("API 使用示例完成")


def main():
    """主函数"""
    print("火山引擎 TLS 日志使用演示")
    print("=" * 50)
    
    # 演示配置格式
    demo_nacos_config_format()
    
    # 演示 TLS 日志配置
    demo_tls_logging_with_config()
    
    # 演示最简配置
    demo_tls_logging_minimal()
    
    # 演示 API 用法
    demo_logger_api_usage()
    
    print("\n=" * 50)
    print("演示完成！")
    print("\n使用要点：")
    print("1. 在 Nacos 中配置 tls.log.config 包含火山引擎认证信息")
    print("2. 初始化时传入 topic_id（必需）和 service_name（可选）")
    print("3. 每个服务使用不同的 TopicID")
    print("4. 日志会自动包含 TraceID 和服务信息")


if __name__ == "__main__":
    main() 