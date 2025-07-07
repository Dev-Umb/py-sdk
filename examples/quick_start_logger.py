"""
日志系统快速开始示例

这个示例展示了如何用最简单的方式使用日志系统
"""

# 添加当前目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. 导入必要的模块
from context.manager import create_context
from logger import init_logger, get_logger


def main():
    """快速开始示例"""
    print("日志系统快速开始")
    print("=" * 30)
    
    # 2. 在应用启动时初始化日志系统（只需要调用一次）
    init_logger()
    
    # 3. 在任何地方获取logger实例
    logger = get_logger(__name__)
    
    # 4. 创建上下文
    ctx = create_context()
    
    # 5. 记录日志
    logger.info(ctx, "应用启动成功")
    logger.warning(ctx, "这是一条警告信息")
    logger.error(ctx, "这是一条错误信息")
    
    # 6. 记录带额外信息的日志
    logger.info(ctx, "用户登录", extra={
        "user_id": "12345",
        "ip": "192.168.1.100"
    })
    
    print("日志记录完成！")


# 模拟在其他模块中使用logger
def other_module_function():
    """模拟其他模块中的函数"""
    # 直接获取logger，不需要重新初始化
    logger = get_logger("other_module")
    ctx = create_context()
    
    logger.info(ctx, "来自其他模块的日志")


if __name__ == "__main__":
    main()
    other_module_function()
    
    print("\n使用要点：")
    print("1. 只需要在应用启动时调用一次 init_logger()")
    print("2. 在任何地方使用 get_logger(__name__) 获取logger")
    print("3. 使用 logger.info(context, message) 记录日志")
    print("4. 日志会自动包含 TraceID") 