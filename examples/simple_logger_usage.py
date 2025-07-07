"""
简化的日志使用示例

展示如何使用新的简化API来初始化和使用日志系统
"""

# 添加当前目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context.manager import create_context
from logger import init_logger, get_logger, is_logger_initialized


def demo_simple_usage():
    """演示最简单的使用方法"""
    print("=== 最简单的使用方法 ===")
    
    # 1. 在应用启动时初始化一次（最简单的配置）
    init_logger()
    
    print(f"日志是否已初始化: {is_logger_initialized()}")
    
    # 2. 在任何地方获取logger（不需要重新初始化）
    logger = get_logger(__name__)
    
    # 3. 创建上下文并记录日志
    ctx = create_context()
    logger.info(ctx, "这是一条简单的日志")
    logger.warning(ctx, "这是一条警告日志")
    logger.error(ctx, "这是一条错误日志")


def demo_in_different_module():
    """演示在不同模块中使用logger"""
    print("\n=== 在不同模块中使用 ===")
    
    # 模拟在不同模块中使用logger
    # 注意：不需要重新初始化，直接获取即可
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    logger3 = get_logger("module3")
    
    ctx = create_context()
    
    logger1.info(ctx, "来自模块1的日志")
    logger2.info(ctx, "来自模块2的日志")
    logger3.info(ctx, "来自模块3的日志")
    
    print("多个模块都可以正常使用logger")


def demo_with_file_output():
    """演示带文件输出的配置"""
    print("\n=== 带文件输出的配置 ===")
    
    # 重新初始化（实际上会被忽略，因为已经初始化过了）
    init_logger(
        level="DEBUG",
        console=True,
        file="demo.log"  # 启用文件输出
    )
    
    logger = get_logger("file-demo")
    ctx = create_context()
    
    logger.debug(ctx, "这是调试日志")
    logger.info(ctx, "这是信息日志")
    logger.warning(ctx, "这是警告日志")
    
    print("日志已记录到文件: demo.log")


def demo_with_tls():
    """演示TLS配置"""
    print("\n=== TLS配置示例 ===")
    
    # 这个初始化会被忽略，因为logger已经初始化过了
    init_logger(
        level="INFO",
        console=True,
        tls=True,
        topic_id="your-topic-id",
        service_name="demo-service"
    )
    
    logger = get_logger("tls-demo")
    ctx = create_context()
    
    logger.info(ctx, "这条日志会发送到TLS（如果配置正确）")


def demo_business_logic():
    """演示在业务逻辑中使用logger"""
    print("\n=== 业务逻辑中使用 ===")
    
    def process_order(order_id: str):
        """处理订单的业务逻辑"""
        logger = get_logger("order_service")
        ctx = create_context()
        
        logger.info(ctx, f"开始处理订单: {order_id}")
        
        try:
            # 模拟业务处理
            if order_id == "invalid":
                raise ValueError("无效的订单ID")
            
            logger.info(ctx, f"订单处理成功: {order_id}", extra={
                "order_id": order_id,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(ctx, f"订单处理失败: {order_id}", extra={
                "order_id": order_id,
                "error": str(e)
            })
            logger.exception(ctx, "订单处理异常详情")
    
    def user_login(user_id: str):
        """用户登录的业务逻辑"""
        logger = get_logger("user_service")
        ctx = create_context()
        
        logger.info(ctx, f"用户登录: {user_id}", extra={
            "user_id": user_id,
            "action": "login"
        })
    
    # 执行业务逻辑
    process_order("ORD-001")
    process_order("invalid")
    user_login("user123")


def main():
    """主函数"""
    print("简化的日志使用演示")
    print("=" * 50)
    
    # 演示各种使用方式
    demo_simple_usage()
    demo_in_different_module()
    demo_with_file_output()
    demo_with_tls()
    demo_business_logic()
    
    print("\n=" * 50)
    print("演示完成！")
    print("\n关键要点：")
    print("1. 只需要在应用启动时调用一次 init_logger()")
    print("2. 在任何地方都可以使用 get_logger(__name__) 获取logger")
    print("3. 重复初始化会被自动忽略")
    print("4. 每个模块可以使用不同的logger名称")
    print("5. 所有logger共享同一个配置")


if __name__ == "__main__":
    main() 