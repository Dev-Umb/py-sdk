#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py_sdk 完整使用示例

演示如何集成使用 py_sdk 的所有核心模块：
- context: 上下文管理和 TraceID
- logger: 日志管理
- http_client: HTTP 响应格式
- nacos_sdk: 服务注册发现和配置管理
"""

import os
import time
from context import create_context
from logger import init_logger_manager, get_logger
from http_client import create_response, OK, INVALID_PARAMS, BusinessCode
from nacos_sdk import registerNacos, unregisterNacos, get_config


def main():
    """主函数 - 完整功能演示"""
    print("🎯 py_sdk 完整使用示例")
    print("=" * 60)
    
    # 1. 初始化系统
    print("\n📋 1. 系统初始化")
    initialize_system()
    
    # 2. 服务注册
    print("\n📋 2. 服务注册")
    service_info = register_service()
    
    # 3. 配置管理
    print("\n📋 3. 配置管理")
    config = load_configuration()
    
    # 4. 模拟 Web API 服务
    print("\n📋 4. 模拟 Web API 服务")
    simulate_web_api_service(config)
    
    # 5. 模拟微服务调用
    print("\n📋 5. 模拟微服务调用")
    simulate_microservice_calls()
    
    # 6. 清理资源
    print("\n📋 6. 清理资源")
    cleanup_resources(service_info)
    
    print("\n" + "=" * 60)
    print("✅ 完整示例演示完成！")
    print("\n🌟 py_sdk 核心特性：")
    print("• 自动 TraceID 生成和传递")
    print("• 统一的日志格式和结构化记录")
    print("• 标准化的 HTTP 响应格式")
    print("• 简化的服务注册发现")
    print("• 开箱即用的微服务工具链")


def initialize_system():
    """初始化系统"""
    # 设置环境变量
    os.environ.setdefault('NACOS_SERVER_ADDRESSES', '127.0.0.1:8848')
    os.environ.setdefault('NACOS_NAMESPACE', 'dev')
    
    # 初始化日志管理器
    init_logger_manager(
        config={
            "level": "INFO",
            "handlers": {
                "console": {"enabled": True}
            }
        },
        service_name="complete-example"
    )
    
    logger = get_logger("system")
    ctx = create_context()
    
    logger.info( "系统初始化完成", extra={
        "components": ["context", "logger", "http_client", "nacos_sdk"],
        "version": "1.0.0"
    })
    
    print("✅ 系统组件初始化完成")


def register_service():
    """注册服务"""
    logger = get_logger("service")
    ctx = create_context()
    
    service_info = {
        "name": "py-sdk-demo",
        "port": 8080,
        "version": "1.0.0"
    }
    
    logger.info( "开始注册服务", extra=service_info)
    
    success = registerNacos(
        service_name=service_info["name"],
        port=service_info["port"],
        metadata={
            "version": service_info["version"],
            "framework": "py_sdk",
            "team": "backend"
        }
    )
    
    if success:
        print(f"✅ 服务 {service_info['name']} 注册成功")
        logger.info( "服务注册成功")
    else:
        print(f"❌ 服务 {service_info['name']} 注册失败")
        logger.error( "服务注册失败")
    
    return service_info


def load_configuration():
    """加载配置"""
    logger = get_logger("config")
    ctx = create_context()
    
    logger.info( "开始加载配置")
    
    # 尝试从 Nacos 获取配置
    config_items = {
        "database": ("database.json", "DEFAULT_GROUP"),
        "redis": ("redis.json", "DEFAULT_GROUP"),
        "app": ("application.properties", "DEFAULT_GROUP")
    }
    
    config = {}
    for key, (data_id, group) in config_items.items():
        config_value = get_config(data_id, group)
        if config_value:
            config[key] = config_value
            logger.info( "配置加载成功", extra={
                "config_key": key,
                "data_id": data_id
            })
            print(f"   ✅ {key} 配置加载成功")
        else:
            logger.warning( "配置不存在", extra={
                "config_key": key,
                "data_id": data_id
            })
            print(f"   ⚠️  {key} 配置不存在，使用默认配置")
    
    # 使用默认配置
    if not config:
        config = {
            "database": {"host": "localhost", "port": 3306},
            "redis": {"host": "localhost", "port": 6379},
            "app": {"debug": True, "max_connections": 100}
        }
        logger.info( "使用默认配置")
        print("   ✅ 使用默认配置")
    
    return config


def simulate_web_api_service(config):
    """模拟 Web API 服务"""
    logger = get_logger("api")
    
    # 模拟处理不同的 API 请求
    api_requests = [
        {"method": "GET", "path": "/users/123", "user_id": 123},
        {"method": "POST", "path": "/users", "data": {"name": "张三", "email": "zhangsan@example.com"}},
        {"method": "GET", "path": "/users/0", "user_id": 0},  # 参数错误
        {"method": "GET", "path": "/users/999", "user_id": 999}  # 用户不存在
    ]
    
    for request in api_requests:
        ctx = create_context()
        
        logger.info( "收到 API 请求", extra={
            "method": request["method"],
            "path": request["path"],
            "user_agent": "py_sdk_demo/1.0.0"
        })
        
        # 处理请求
        response = handle_api_request(ctx, request)
        
        logger.info( "API 请求处理完成", extra={
            "method": request["method"],
            "path": request["path"],
            "response_code": response.code,
            "success": response.is_success()
        })
        
        print(f"   📤 {request['method']} {request['path']} -> {response.code}")


def handle_api_request(ctx, request):
    """处理 API 请求"""
    logger = get_logger("handler")
    
    # 自定义业务状态码
    USER_NOT_FOUND = BusinessCode(
        code=20001,
        message="用户不存在",
        i18n="user_not_found"
    )
    
    if request["method"] == "GET" and "/users/" in request["path"]:
        user_id = request.get("user_id", 0)
        
        # 参数验证
        if user_id <= 0:
            logger.warning( "参数验证失败", extra={"user_id": user_id})
            return create_response(
                context=ctx,
                code=INVALID_PARAMS,
                data={"field": "user_id", "message": "用户ID必须大于0"}
            )
        
        # 模拟业务逻辑
        if user_id == 999:
            logger.warning( "用户不存在", extra={"user_id": user_id})
            return create_response(
                context=ctx,
                code=USER_NOT_FOUND,
                data={"user_id": user_id}
            )
        
        # 成功响应
        user_data = {"id": user_id, "name": "张三", "status": "active"}
        logger.info( "用户信息获取成功", extra={"user_id": user_id})
        return create_response(
            context=ctx,
            code=OK,
            data=user_data
        )
    
    elif request["method"] == "POST" and request["path"] == "/users":
        # 创建用户
        user_data = request.get("data", {})
        new_user = {"id": 12345, **user_data, "created_at": time.time()}
        
        logger.info( "用户创建成功", extra={"user_id": new_user["id"]})
        return create_response(
            context=ctx,
            code=OK,
            data=new_user
        )
    
    # 默认响应
    return create_response(
        context=ctx,
        code=OK,
        data={"message": "请求处理完成"}
    )


def simulate_microservice_calls():
    """模拟微服务调用"""
    logger = get_logger("microservice")
    
    services = [
        {"name": "user-service", "operation": "获取用户信息"},
        {"name": "order-service", "operation": "创建订单"},
        {"name": "payment-service", "operation": "处理支付"},
        {"name": "notification-service", "operation": "发送通知"}
    ]
    
    # 模拟完整的业务流程
    ctx = create_context()
    logger.info( "开始业务流程", extra={
        "flow_name": "order_processing",
        "services_count": len(services)
    })
    
    for i, service in enumerate(services, 1):
        # 模拟服务调用
        logger.info( "调用微服务", extra={
            "service_name": service["name"],
            "operation": service["operation"],
            "step": i,
            "total_steps": len(services)
        })
        
        # 模拟处理时间
        time.sleep(0.5)
        
        # 模拟响应
        response = create_response(
            context=ctx,
            code=OK,
            data={
                "service": service["name"],
                "operation": service["operation"],
                "result": "success",
                "timestamp": time.time()
            }
        )
        
        logger.info( "微服务调用成功", extra={
            "service_name": service["name"],
            "response_code": response.code
        })
        
        print(f"   ✅ {service['name']} - {service['operation']}")
    
    logger.info( "业务流程完成", extra={
        "flow_name": "order_processing",
        "status": "completed"
    })
    print("   🎉 完整业务流程执行成功")


def cleanup_resources(service_info):
    """清理资源"""
    logger = get_logger("cleanup")
    ctx = create_context()
    
    logger.info( "开始清理资源")
    
    # 注销服务
    success = unregisterNacos(
        service_name=service_info["name"],
        port=service_info["port"]
    )
    
    if success:
        print(f"✅ 服务 {service_info['name']} 注销成功")
        logger.info( "服务注销成功")
    else:
        print(f"❌ 服务 {service_info['name']} 注销失败")
        logger.error( "服务注销失败")
    
    logger.info( "资源清理完成")
    print("✅ 资源清理完成")


if __name__ == "__main__":
    main() 