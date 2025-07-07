#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 客户端模块示例

演示如何使用 http_client 模块创建标准化的 API 响应，
包括成功响应、错误响应、自定义状态码等功能。
"""

from context import create_context
from http_client import (
    create_response, 
    BusinessCode, 
    OK, 
    INTERNAL_SERVER_ERROR,
    ROOM_NOT_FOUND, 
    UNAUTHORIZED, 
    INVALID_PARAMS
)


def main():
    """主函数"""
    print("🌐 HTTP 客户端模块示例")
    print("=" * 50)
    
    # 1. 基础响应创建
    print("\n📋 1. 基础响应创建")
    basic_response()
    
    # 2. 错误响应
    print("\n📋 2. 错误响应")
    error_response()
    
    # 3. 自定义业务状态码
    print("\n📋 3. 自定义业务状态码")
    custom_business_code()
    
    # 4. API 处理流程
    print("\n📋 4. API 处理流程")
    api_processing_flow()
    
    # 5. 微服务调用示例
    print("\n📋 5. 微服务调用示例")
    microservice_call_example()
    
    print("\n" + "=" * 50)
    print("✅ HTTP 客户端示例完成！")


def basic_response():
    """基础响应创建示例"""
    print("创建基础响应...")
    
    # 创建上下文
    ctx = create_context()
    
    # 成功响应（默认使用 OK）
    response = create_response(
        context=ctx,
        data={"message": "Hello World", "id": 123}
    )
    
    print("✓ 成功响应创建完成")
    print(f"  响应内容: {response.to_json()}")
    print(f"  是否成功: {response.is_success()}")
    print(f"  TraceID: {response.trace_id}")
    
    # 仅消息响应
    simple_response = create_response(
        context=ctx,
        data={"status": "服务运行正常"}
    )
    
    print(f"\n✓ 简单响应: {simple_response.to_dict()}")


def error_response():
    """错误响应示例"""
    print("创建错误响应...")
    
    ctx = create_context()
    
    # 房间不存在错误
    room_error = create_response(
        context=ctx,
        code=ROOM_NOT_FOUND
    )
    
    print("✓ 房间不存在错误响应:")
    print(f"  {room_error.to_json()}")
    print(f"  是否错误: {room_error.is_error()}")
    
    # 未授权错误
    auth_error = create_response(
        context=ctx,
        code=UNAUTHORIZED
    )
    
    print(f"\n✓ 未授权错误响应:")
    print(f"  {auth_error.to_dict()}")
    
    # 参数错误
    param_error = create_response(
        context=ctx,
        code=INVALID_PARAMS,
        data={"field": "user_id", "message": "用户ID不能为空"}
    )
    
    print(f"\n✓ 参数错误响应:")
    print(f"  {param_error.to_dict()}")
    
    # 内部服务器错误
    server_error = create_response(
        context=ctx,
        code=INTERNAL_SERVER_ERROR
    )
    
    print(f"\n✓ 内部服务器错误响应:")
    print(f"  {server_error.to_dict()}")


def custom_business_code():
    """自定义业务状态码示例"""
    print("创建自定义业务状态码...")
    
    # 定义自定义业务状态码
    USER_NOT_FOUND = BusinessCode(20001, "用户不存在", "user_not_found")
    INSUFFICIENT_BALANCE = BusinessCode(20002, "余额不足", "insufficient_balance")
    ORDER_EXPIRED = BusinessCode(20003, "订单已过期", "order_expired")
    PRODUCT_OUT_OF_STOCK = BusinessCode(20004, "商品库存不足", "product_out_of_stock")
    
    ctx = create_context()
    
    # 使用自定义状态码
    user_error = create_response(
        context=ctx,
        code=USER_NOT_FOUND,
        data={"user_id": 12345}
    )
    
    print("✓ 用户不存在错误:")
    print(f"  {user_error.to_json()}")
    
    # 余额不足错误
    balance_error = create_response(
        context=ctx,
        code=INSUFFICIENT_BALANCE,
        data={
            "user_id": 12345,
            "required_amount": 100.00,
            "current_balance": 50.00
        }
    )
    
    print(f"\n✓ 余额不足错误:")
    print(f"  {balance_error.to_dict()}")
    
    # 订单过期错误
    order_error = create_response(
        context=ctx,
        code=ORDER_EXPIRED,
        data={
            "order_id": "ORD-2023-001",
            "expired_at": "2023-12-01 10:00:00"
        }
    )
    
    print(f"\n✓ 订单过期错误:")
    print(f"  {order_error.to_dict()}")


def api_processing_flow():
    """API 处理流程示例"""
    print("模拟 API 处理流程...")
    
    # 模拟用户查询 API
    user_query_api()
    
    # 模拟订单创建 API
    order_create_api()
    
    # 模拟支付处理 API
    payment_process_api()


def user_query_api():
    """用户查询 API 示例"""
    print("\n  用户查询 API:")
    
    ctx = create_context()
    user_id = 12345
    
    try:
        # 模拟参数验证
        if user_id <= 0:
            response = create_response(
                context=ctx,
                code=INVALID_PARAMS,
                data={"field": "user_id", "message": "用户ID必须大于0"}
            )
            print(f"    参数错误: {response.to_dict()}")
            return
        
        # 模拟查询用户
        user_data = {
            "id": user_id,
            "name": "张三",
            "email": "zhangsan@example.com",
            "status": "active"
        }
        
        # 成功响应
        response = create_response(
            context=ctx,
            code=OK,
            data=user_data
        )
        
        print(f"    查询成功: {response.to_dict()}")
        
    except Exception as e:
        # 异常响应
        error_response = create_response(
            context=ctx,
            code=INTERNAL_SERVER_ERROR
        )
        print(f"    系统异常: {error_response.to_dict()}")


def order_create_api():
    """订单创建 API 示例"""
    print("\n  订单创建 API:")
    
    ctx = create_context()
    
    try:
        # 模拟订单创建
        order_data = {
            "order_id": "ORD-2023-001",
            "user_id": 12345,
            "amount": 99.99,
            "currency": "CNY",
            "status": "created",
            "created_at": "2023-12-01 10:00:00"
        }
        
        # 成功响应
        response = create_response(
            context=ctx,
            code=OK,
            data=order_data
        )
        
        print(f"    订单创建成功: {response.to_dict()}")
        
    except Exception as e:
        # 异常响应
        error_response = create_response(
            context=ctx,
            code=INTERNAL_SERVER_ERROR
        )
        print(f"    创建失败: {error_response.to_dict()}")


def payment_process_api():
    """支付处理 API 示例"""
    print("\n  支付处理 API:")
    
    ctx = create_context()
    
    # 定义支付相关状态码
    PAYMENT_FAILED = BusinessCode(30001, "支付失败", "payment_failed")
    INSUFFICIENT_BALANCE = BusinessCode(30002, "余额不足", "insufficient_balance")
    
    try:
        # 模拟余额检查
        user_balance = 50.00
        payment_amount = 100.00
        
        if user_balance < payment_amount:
            response = create_response(
                context=ctx,
                code=INSUFFICIENT_BALANCE,
                data={
                    "required_amount": payment_amount,
                    "current_balance": user_balance,
                    "shortage": payment_amount - user_balance
                }
            )
            print(f"    余额不足: {response.to_dict()}")
            return
        
        # 模拟支付成功
        payment_data = {
            "payment_id": "PAY-2023-001",
            "order_id": "ORD-2023-001",
            "amount": payment_amount,
            "status": "success",
            "payment_method": "alipay",
            "transaction_id": "TXN-123456789"
        }
        
        response = create_response(
            context=ctx,
            code=OK,
            data=payment_data
        )
        
        print(f"    支付成功: {response.to_dict()}")
        
    except Exception as e:
        # 支付失败
        error_response = create_response(
            context=ctx,
            code=PAYMENT_FAILED,
            data={"error": str(e)}
        )
        print(f"    支付失败: {error_response.to_dict()}")


def microservice_call_example():
    """微服务调用示例"""
    print("模拟微服务调用...")
    
    # 模拟用户服务调用
    user_service_call()
    
    # 模拟订单服务调用
    order_service_call()
    
    # 模拟库存服务调用
    inventory_service_call()


def user_service_call():
    """用户服务调用示例"""
    print("\n  调用用户服务:")
    
    ctx = create_context()
    
    def get_user_info(user_id):
        """获取用户信息"""
        try:
            if user_id == 12345:
                return create_response(
                    context=ctx,
                    code=OK,
                    data={
                        "id": user_id,
                        "name": "张三",
                        "level": "VIP",
                        "balance": 500.00
                    }
                )
            else:
                USER_NOT_FOUND = BusinessCode(20001, "用户不存在", "user_not_found")
                return create_response(
                    context=ctx,
                    code=USER_NOT_FOUND,
                    data={"user_id": user_id}
                )
        except Exception:
            return create_response(
                context=ctx,
                code=INTERNAL_SERVER_ERROR
            )
    
    # 调用用户服务
    response = get_user_info(12345)
    print(f"    用户信息查询: {response.to_dict()}")
    
    response = get_user_info(99999)
    print(f"    用户不存在: {response.to_dict()}")


def order_service_call():
    """订单服务调用示例"""
    print("\n  调用订单服务:")
    
    ctx = create_context()
    
    def create_order(user_id, product_id, quantity):
        """创建订单"""
        try:
            order_data = {
                "order_id": "ORD-2023-002",
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": 99.99,
                "total_amount": 99.99 * quantity,
                "status": "pending"
            }
            
            return create_response(
                context=ctx,
                code=OK,
                data=order_data
            )
        except Exception:
            return create_response(
                context=ctx,
                code=INTERNAL_SERVER_ERROR
            )
    
    # 调用订单服务
    response = create_order(12345, "PROD-001", 2)
    print(f"    订单创建: {response.to_dict()}")


def inventory_service_call():
    """库存服务调用示例"""
    print("\n  调用库存服务:")
    
    ctx = create_context()
    
    def check_inventory(product_id, quantity):
        """检查库存"""
        try:
            # 模拟库存检查
            available_stock = 5
            
            if available_stock >= quantity:
                return create_response(
                    context=ctx,
                    code=OK,
                    data={
                        "product_id": product_id,
                        "available_stock": available_stock,
                        "requested_quantity": quantity,
                        "sufficient": True
                    }
                )
            else:
                INSUFFICIENT_STOCK = BusinessCode(40001, "库存不足", "insufficient_stock")
                return create_response(
                    context=ctx,
                    code=INSUFFICIENT_STOCK,
                    data={
                        "product_id": product_id,
                        "available_stock": available_stock,
                        "requested_quantity": quantity,
                        "shortage": quantity - available_stock
                    }
                )
        except Exception:
            return create_response(
                context=ctx,
                code=INTERNAL_SERVER_ERROR
            )
    
    # 调用库存服务
    response = check_inventory("PROD-001", 2)
    print(f"    库存检查: {response.to_dict()}")
    
    response = check_inventory("PROD-001", 10)
    print(f"    库存不足: {response.to_dict()}")


if __name__ == "__main__":
    main() 