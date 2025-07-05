"""
基础使用示例

演示 py-sdk 的基本功能使用方法，包括内网 Nacos 集成。
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, '.')

from context.manager import create_context, set_context, get_current_context
from logger import init_logger_manager, get_logger
from http_client.response import create_response
from http_client.client import HttpClient
from http_client.code import OK, INVALID_PARAMS, ROOM_NOT_FOUND, INTERNAL_SERVER_ERROR
from nacos.api import get_config
from nacos.client import NacosClient


def setup_nacos_environment():
    """设置 Nacos 环境变量"""
    print("=== 设置 Nacos 环境 ===")
    
    # 设置内网 Nacos 地址
    os.environ['NACOS_ADDRESS'] = '10.15.101.239:8848'
    os.environ['NACOS_NAMESPACE'] = ''  # 使用默认命名空间
    
    print(f"✅ Nacos 地址: {os.environ['NACOS_ADDRESS']}")
    print(f"✅ 命名空间: {os.environ.get('NACOS_NAMESPACE', '默认')}")
    print()


def init_logger_from_nacos():
    """从 Nacos 获取配置并初始化 Logger"""
    print("=== 初始化 Logger ===")
    
    try:
        # 尝试从 Nacos 获取 logger 配置
        logger_config_str = get_config("logger.json")
        if logger_config_str:
            logger_config = json.loads(logger_config_str)
            print("✅ 从 Nacos 获取 logger 配置成功")
        else:
            # 使用默认配置
            logger_config = {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s",
                "handlers": {
                    "console": {
                        "enabled": True,
                        "level": "INFO"
                    },
                    "file": {
                        "enabled": True,
                        "level": "DEBUG",
                        "filename": "basic-usage.log",
                        "max_bytes": 10485760,
                        "backup_count": 5
                    },
                    "tls": {
                        "enabled": False,  # 默认关闭 TLS，避免认证错误
                        "level": "INFO"
                    }
                }
            }
            print("⚠️  未获取到 Nacos logger 配置，使用默认配置")
        
        # 初始化 logger
        init_logger_manager(
            config=logger_config,
            topic_id="basic-usage-logs",
            service_name="basic-usage-demo"
        )
        print("✅ Logger 初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ Logger 初始化失败: {str(e)}")
        # 使用最简配置作为备用
        init_logger_manager(
            config={"handlers": {"console": {"enabled": True}}},
            topic_id="basic-usage-logs",
            service_name="basic-usage-demo"
        )
        return False


def basic_context_usage():
    """基础上下文使用示例"""
    print("=== 上下文管理示例 ===")
    
    # 创建上下文（自动生成 TraceID）
    ctx = create_context()
    print(f"✅ 创建上下文成功")
    print(f"   TraceID: {ctx.trace_id}")
    print(f"   创建时间: {ctx.created_at}")
    
    # 设置上下文
    set_context(ctx)
    print("✅ 设置上下文成功")
    
    # 获取当前上下文
    current_ctx = get_current_context()
    print(f"✅ 获取当前上下文: {current_ctx.trace_id == ctx.trace_id}")
    
    # 创建带自定义 TraceID 的上下文
    custom_ctx = create_context(trace_id="custom-trace-123")
    print(f"✅ 自定义 TraceID: {custom_ctx.trace_id}")
    
    print()


def basic_logger_usage():
    """基础日志使用示例"""
    print("=== 日志管理示例 ===")
    
    # 获取日志记录器
    logger = get_logger("basic-example")
    
    # 获取当前上下文
    ctx = get_current_context()
    if not ctx:
        ctx = create_context()
        set_context(ctx)
    
    print(f"使用 TraceID: {ctx.trace_id}")
    
    # 记录各级别日志
    logger.debug(ctx, "这是调试信息")
    logger.info(ctx, "这是普通信息")
    logger.warning(ctx, "这是警告信息")
    logger.error(ctx, "这是错误信息")
    
    # 记录带额外参数的日志
    logger.info(ctx, "用户操作", extra={
        "user_id": 12345,
        "action": "login",
        "ip": "192.168.1.100"
    })
    
    # 业务流程日志
    logger.info(ctx, "开始处理订单", extra={
        "order_id": "ORDER-001",
        "amount": 99.99
    })
    
    time.sleep(0.1)  # 模拟处理时间
    
    logger.info(ctx, "订单处理完成", extra={
        "order_id": "ORDER-001",
        "status": "completed"
    })
    
    # 异常日志示例
    try:
        result = 1 / 0
    except Exception:
        logger.exception(ctx, "计算异常", extra={
            "operation": "division",
            "dividend": 1,
            "divisor": 0,
            "error_type": "ZeroDivisionError"
        })
    
    print("✅ 日志记录完成")
    print()


def basic_http_response_usage():
    """基础HTTP响应使用示例"""
    print("=== HTTP 响应示例 ===")
    
    # 获取当前上下文
    ctx = get_current_context()
    if not ctx:
        ctx = create_context()
        set_context(ctx)
    
    print(f"使用 TraceID: {ctx.trace_id}")
    
    # 1. 默认成功响应
    success_resp = create_response(ctx, data={"id": 1, "name": "测试数据"})
    print("✅ 成功响应:")
    print(f"   {success_resp.to_json()}")
    print()
    
    # 2. 错误响应（自动使用 code 的 message）
    error_resp = create_response(ctx, code=INVALID_PARAMS)
    print("✅ 错误响应:")
    print(f"   {error_resp.to_json()}")
    print()
    
    # 3. 房间不存在错误
    room_error = create_response(ctx, code=ROOM_NOT_FOUND)
    print("✅ 房间不存在响应:")
    print(f"   {room_error.to_json()}")
    print()
    
    # 4. 带数据的错误响应
    param_error = create_response(
        ctx, 
        code=INVALID_PARAMS, 
        data={"field": "room_id", "value": -1}
    )
    print("✅ 带数据的错误响应:")
    print(f"   {param_error.to_json()}")
    print()
    
    # 5. 分页数据响应
    paginated_data = {
        "items": [{"id": i, "name": f"项目{i}"} for i in range(1, 6)],
        "pagination": {
            "total": 50,
            "page": 1,
            "page_size": 5,
            "total_pages": 10,
            "has_next": True,
            "has_prev": False
        }
    }
    
    page_response = create_response(ctx, data=paginated_data)
    print("✅ 分页响应:")
    print(f"   {page_response.to_json()}")
    print()


def basic_http_client_usage():
    """基础HTTP客户端使用示例"""
    print("=== HTTP 客户端示例 ===")
    
    # 创建HTTP客户端
    client = HttpClient()
    
    # 发起GET请求（使用公共API）
    try:
        print("发起 GET 请求...")
        response = client.get("https://httpbin.org/get", params={"test": "value"})
        print(f"✅ GET 请求结果: {response.code} - {response.message}")
        if response.is_success():
            print("   请求成功")
        else:
            print("   请求失败")
    except Exception as e:
        print(f"❌ GET 请求异常: {str(e)}")
    
    # 发起POST请求
    try:
        print("发起 POST 请求...")
        post_data = {"name": "测试", "value": 123}
        response = client.post("https://httpbin.org/post", json=post_data)
        print(f"✅ POST 请求结果: {response.code} - {response.message}")
    except Exception as e:
        print(f"❌ POST 请求异常: {str(e)}")
    
    print()


def basic_nacos_config_usage():
    """基础Nacos配置使用示例"""
    print("=== Nacos 配置示例 ===")
    
    # 获取各种配置
    configs_to_test = ["logger.json", "tls.log.config", "services.json", "app.config"]
    
    for config_name in configs_to_test:
        try:
            config = get_config(config_name)
            if config:
                print(f"✅ {config_name}: 已配置 ({len(config)} 字符)")
                # 如果是 JSON 配置，尝试解析
                if config_name.endswith('.json'):
                    try:
                        config_data = json.loads(config)
                        print(f"   配置项数量: {len(config_data) if isinstance(config_data, dict) else 'N/A'}")
                    except:
                        pass
            else:
                print(f"❌ {config_name}: 未配置")
        except Exception as e:
            print(f"❌ {config_name}: 获取失败 - {str(e)}")
    
    print()


def test_nacos_operations():
    """测试 Nacos 操作"""
    print("=== Nacos 操作测试 ===")
    
    try:
        client = NacosClient()
        
        # 1. 发布一个测试配置
        test_config = {
            "app_name": "basic-usage-demo",
            "version": "1.0.0",
            "debug": True,
            "test_timestamp": time.time()
        }
        
        success = client.publish_config(
            data_id="test.config",
            content=json.dumps(test_config, indent=2),
            group="DEFAULT_GROUP"
        )
        
        if success:
            print("✅ 发布测试配置成功")
        else:
            print("❌ 发布测试配置失败")
        
        # 2. 获取刚发布的配置
        time.sleep(0.5)  # 等待配置同步
        retrieved_config = get_config("test.config")
        if retrieved_config:
            print("✅ 获取测试配置成功")
            config_data = json.loads(retrieved_config)
            print(f"   应用名称: {config_data.get('app_name')}")
            print(f"   版本: {config_data.get('version')}")
        else:
            print("❌ 获取测试配置失败")
        
        return True
        
    except Exception as e:
        print(f"❌ Nacos 操作异常: {str(e)}")
        return False


async def async_context_usage():
    """异步上下文使用示例"""
    print("=== 异步上下文示例 ===")
    
    # 创建上下文
    ctx = create_context()
    set_context(ctx)
    
    logger = get_logger("async-example")
    logger.info(ctx, "开始异步操作")
    
    print(f"主协程 TraceID: {ctx.trace_id}")
    
    # 模拟异步操作
    await asyncio.sleep(0.1)
    
    # 在异步函数中获取上下文
    current_ctx = get_current_context()
    logger.info(current_ctx, "异步操作中")
    print(f"异步中 TraceID: {current_ctx.trace_id}")
    
    # 调用其他异步函数
    await another_async_function()
    
    logger.info(ctx, "异步操作完成")
    print("✅ 异步上下文测试完成")
    print()


async def another_async_function():
    """另一个异步函数"""
    # 在嵌套的异步函数中也能获取到上下文
    ctx = get_current_context()
    logger = get_logger("async-nested")
    logger.info(ctx, "在嵌套异步函数中")
    print(f"嵌套协程 TraceID: {ctx.trace_id}")


def simulate_request_processing():
    """模拟请求处理流程"""
    print("=== 模拟请求处理流程 ===")
    
    # 1. 创建请求上下文（通常由中间件完成）
    ctx = create_context()
    set_context(ctx)
    
    logger = get_logger("request-processor")
    
    # 2. 记录请求开始
    logger.info(ctx, "开始处理请求", extra={
        "method": "POST",
        "path": "/api/rooms",
        "client_ip": "192.168.1.100"
    })
    
    try:
        # 3. 模拟参数验证
        room_data = {"name": "会议室A", "capacity": 10}
        logger.info(ctx, "参数验证通过", extra=room_data)
        
        # 4. 模拟业务逻辑
        logger.info(ctx, "执行业务逻辑")
        
        # 模拟数据库操作
        time.sleep(0.1)
        logger.info(ctx, "数据库操作完成", extra={
            "operation": "INSERT",
            "table": "rooms",
            "affected_rows": 1
        })
        
        # 5. 创建成功响应
        response = create_response(
            ctx,
            data={
                "id": 123,
                "name": room_data["name"],
                "capacity": room_data["capacity"],
                "created_at": "2024-01-01T12:00:00Z"
            }
        )
        
        # 6. 记录请求完成
        logger.info(ctx, "请求处理成功", extra={
            "response_code": response.code,
            "processing_time_ms": 100
        })
        
        print("✅ 请求处理成功")
        print(f"   响应: {response.to_json()}")
        
    except Exception as e:
        # 异常处理
        logger.exception(ctx, "请求处理失败")
        
        error_response = create_response(ctx, code=INTERNAL_SERVER_ERROR)
        print("❌ 请求处理失败")
        print(f"   错误响应: {error_response.to_json()}")
    
    print()


def main():
    """主函数"""
    print("py-sdk 基础使用示例")
    print("=" * 50)
    print("功能包括：")
    print("- 内网 Nacos 集成 (10.15.101.239:8848)")
    print("- 上下文管理和 TraceID")
    print("- 结构化日志记录")
    print("- HTTP 响应格式化")
    print("- 业务状态码系统")
    print("- HTTP 客户端")
    print("- 异步上下文支持")
    print("=" * 50)
    print()
    
    # 1. 设置环境
    setup_nacos_environment()
    
    # 2. 初始化 Logger
    init_logger_from_nacos()
    
    # 3. 上下文管理
    basic_context_usage()
    
    # 4. 日志功能
    basic_logger_usage()
    
    # 5. HTTP 响应
    basic_http_response_usage()
    
    # 6. HTTP 客户端
    basic_http_client_usage()
    
    # 7. Nacos 配置
    basic_nacos_config_usage()
    
    # 8. Nacos 操作
    test_nacos_operations()
    
    # 9. 请求处理流程
    simulate_request_processing()
    
    # 10. 异步上下文
    print("运行异步上下文示例...")
    asyncio.run(async_context_usage())
    
    print("=" * 50)
    print("✅ 所有示例运行完成！")
    print()
    print("接下来可以：")
    print("1. 查看生成的日志文件: basic-usage.log")
    print("2. 访问 Nacos 控制台: http://10.15.101.239:8848/nacos")
    print("3. 运行 FastAPI 示例: python examples/fastapi_example.py")
    print("4. 查看内网 Nacos 连接示例: python examples/nacos_connection_example.py")


if __name__ == "__main__":
    main() 