#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块示例

演示如何使用 logger 模块进行日志记录，包括基础使用、
结构化日志、异常处理等功能。
"""

import time
from context import create_context
from logger import init_logger_manager, logger


def main():
    """主函数"""
    print("📋 日志管理模块示例")
    print("=" * 50)
    
    # 1. 初始化日志管理器
    print("\n📋 1. 初始化日志管理器")
    init_logging()
    
    # 2. 基础日志记录
    print("\n📋 2. 基础日志记录")
    basic_logging()
    
    # 3. 结构化日志
    print("\n📋 3. 结构化日志")
    structured_logging()
    
    # 4. 异常处理
    print("\n📋 4. 异常处理")
    exception_handling()
    
    # 5. 业务场景示例
    print("\n📋 5. 业务场景示例")
    business_scenario()
    
    print("\n" + "=" * 50)
    print("✅ 日志管理示例完成！")


def init_logging():
    """初始化日志管理器"""
    print("初始化日志管理器...")
    
    # 基础初始化（仅控制台输出）
    init_logger_manager(
        config={
            "level": "INFO",
            "handlers": {
                "console": {"enabled": True}
            }
        },
        service_name="example-service"
    )
    
    print("✓ 日志管理器初始化完成")


def basic_logging():
    """基础日志记录示例"""
    print("基础日志记录...")
    
    # 创建上下文
    ctx = create_context()
    
    # 获取日志记录器
    
    # 记录不同级别的日志
    logger.debug(ctx, "这是调试信息")
    logger.info( "服务启动成功")
    logger.warning( "内存使用率较高")
    logger.error( "数据库连接失败")
    logger.critical(ctx, "系统即将崩溃")
    
    print("✓ 基础日志记录完成")


def structured_logging():
    """结构化日志示例"""
    print("结构化日志记录...")
    
    # 创建上下文
    ctx = create_context()

    # 用户登录日志
    logger.info( "用户登录", extra={
        "user_id": 12345,
        "username": "john_doe",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    })
    
    # 订单创建日志
    logger.info( "订单创建", extra={
        "order_id": "ORD-2023-001",
        "user_id": 12345,
        "amount": 99.99,
        "currency": "CNY",
        "payment_method": "alipay"
    })
    
    # API 调用日志
    logger.info( "API 调用", extra={
        "method": "GET",
        "url": "/api/users/12345",
        "status_code": 200,
        "response_time": 150,
        "user_id": 12345
    })
    
    # 数据库操作日志
    logger.info( "数据库查询", extra={
        "table": "users",
        "operation": "SELECT",
        "query_time": 25,
        "rows_affected": 1
    })
    
    print("✓ 结构化日志记录完成")


def exception_handling():
    """异常处理示例"""
    print("异常处理日志记录...")
    
    # 创建上下文
    ctx = create_context()

    try:
        # 模拟业务异常
        raise ValueError("无效的用户ID")
        
    except ValueError as e:
        logger.error( "业务逻辑错误", extra={
            "error_type": "ValueError",
            "error_message": str(e),
            "user_id": 12345
        })
    
    try:
        # 模拟网络异常
        raise ConnectionError("数据库连接超时")
        
    except ConnectionError as e:
        logger.exception(ctx, "网络连接异常", extra={
            "error_type": "ConnectionError",
            "timeout": 30,
            "retry_count": 3
        })
    
    try:
        # 模拟未知异常
        result = 1 / 0
        
    except Exception as e:
        logger.exception(ctx, "未知异常", extra={
            "operation": "division",
            "input_data": {"a": 1, "b": 0}
        })
    
    print("✓ 异常处理日志记录完成")


def business_scenario():
    """业务场景示例"""
    print("业务场景日志记录...")
    
    # 模拟用户注册流程
    user_registration_flow()
    
    # 模拟订单处理流程
    order_processing_flow()
    
    print("✓ 业务场景日志记录完成")


def user_registration_flow():
    """用户注册流程"""
    ctx = create_context()
    logger.info( "用户注册流程开始", extra={
        "flow": "user_registration",
        "step": "start"
    })
    
    # 步骤1：参数验证
    logger.info( "参数验证", extra={
        "flow": "user_registration",
        "step": "validation",
        "email": "user@example.com",
        "username": "new_user"
    })
    
    time.sleep(0.1)  # 模拟处理时间
    
    # 步骤2：检查用户是否存在
    logger.info( "检查用户唯一性", extra={
        "flow": "user_registration",
        "step": "uniqueness_check",
        "check_result": "passed"
    })
    
    time.sleep(0.1)
    
    # 步骤3：创建用户
    logger.info( "创建用户记录", extra={
        "flow": "user_registration",
        "step": "create_user",
        "user_id": 12345
    })
    
    time.sleep(0.1)
    
    # 步骤4：发送欢迎邮件
    logger.info( "发送欢迎邮件", extra={
        "flow": "user_registration",
        "step": "send_email",
        "email_type": "welcome",
        "user_id": 12345
    })
    
    logger.info( "用户注册流程完成", extra={
        "flow": "user_registration",
        "step": "complete",
        "user_id": 12345,
        "total_time": 400
    })


def order_processing_flow():
    """订单处理流程"""
    ctx = create_context()
    
    order_id = "ORD-2023-001"
    user_id = 12345
    
    logger.info("订单处理流程开始", extra={
        "flow": "order_processing",
        "step": "start",
        "order_id": order_id,
        "user_id": user_id
    })
    
    # 步骤1：库存检查
    logger.info( "库存检查", extra={
        "flow": "order_processing",
        "step": "inventory_check",
        "order_id": order_id,
        "product_id": "PROD-001",
        "quantity": 2,
        "available_stock": 10
    })
    
    time.sleep(0.1)
    
    # 步骤2：价格计算
    logger.info( "价格计算", extra={
        "flow": "order_processing",
        "step": "price_calculation",
        "order_id": order_id,
        "base_price": 99.99,
        "discount": 10.00,
        "final_price": 89.99
    })
    
    time.sleep(0.1)
    
    # 步骤3：支付处理
    logger.info( "支付处理", extra={
        "flow": "order_processing",
        "step": "payment",
        "order_id": order_id,
        "payment_method": "alipay",
        "amount": 89.99,
        "payment_status": "success"
    })
    
    time.sleep(0.2)
    
    # 步骤4：库存扣减
    logger.info( "库存扣减", extra={
        "flow": "order_processing",
        "step": "inventory_deduction",
        "order_id": order_id,
        "product_id": "PROD-001",
        "deducted_quantity": 2,
        "remaining_stock": 8
    })
    
    time.sleep(0.1)
    
    # 步骤5：订单完成
    logger.info( "订单处理完成", extra={
        "flow": "order_processing",
        "step": "complete",
        "order_id": order_id,
        "user_id": user_id,
        "status": "completed",
        "total_time": 500
    })


if __name__ == "__main__":
    main() 