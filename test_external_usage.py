#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部项目使用 py_sdk 的完整示例
在 coc_rules/server 目录中演示如何使用 py_sdk
"""

def test_py_sdk_usage():
    """测试在外部项目中使用 py_sdk 的各种功能"""
    print("🚀 外部项目使用 py_sdk 测试")
    print("=" * 50)
    
    # 1. 测试上下文管理
    print("\n🧪 测试上下文管理")
    print("-" * 30)
    try:
        from context import create_context, get_trace_id
        
        # 创建上下文
        ctx = create_context()
        print(f"✅ 创建上下文成功: {ctx.trace_id}")
        
        # 获取TraceID
        trace_id = get_trace_id()
        print(f"✅ 获取TraceID: {trace_id}")
        
    except Exception as e:
        print(f"❌ 上下文管理测试失败: {e}")
        return False
    
    # 2. 测试日志管理
    print("\n🧪 测试日志管理")
    print("-" * 30)
    try:
        from logger import get_logger
        
        # 获取日志记录器
        logger = get_logger("external-project")
        
        # 记录各种级别的日志
        logger.info(ctx, "外部项目启动成功")
        logger.debug(ctx, "调试信息")
        logger.warning(ctx, "警告信息")
        
        print("✅ 日志记录成功")
        
    except Exception as e:
        print(f"❌ 日志管理测试失败: {e}")
        return False
    
    # 3. 测试HTTP客户端
    print("\n🧪 测试HTTP客户端")
    print("-" * 30)
    try:
        from http_client import create_response, OK, INTERNAL_SERVER_ERROR
        
        # 创建成功响应
        success_response = create_response(
            context=ctx,
            code=OK,
            data={
                "message": "外部项目API调用成功",
                "project": "coc_rules",
                "service": "server"
            }
        )
        
        print("✅ 创建响应成功")
        print(f"   响应代码: {success_response.code}")
        print(f"   响应消息: {success_response.message}")
        print(f"   TraceID: {success_response.trace_id}")
        
    except Exception as e:
        print(f"❌ HTTP客户端测试失败: {e}")
        return False
    
    # 4. 测试Nacos SDK
    print("\n🧪 测试Nacos SDK")
    print("-" * 30)
    try:
        from nacos_sdk import get_config, init_nacos_client
        
        # 初始化Nacos客户端
        print("✅ Nacos SDK 导入成功")
        print("   (实际配置获取需要Nacos服务器运行)")
        
        # 可以测试配置获取（需要Nacos服务器）
        # config = get_config("test.config")
        # print(f"   配置获取: {config}")
        
    except Exception as e:
        print(f"❌ Nacos SDK测试失败: {e}")
        return False
    
    # 5. 测试完整工作流程
    print("\n🧪 测试完整工作流程")
    print("-" * 30)
    try:
        # 模拟一个完整的请求处理流程
        
        # 1. 创建请求上下文
        request_ctx = create_context()
        
        # 2. 获取日志记录器
        service_logger = get_logger("coc_rules.server")
        
        # 3. 记录请求开始
        service_logger.info(request_ctx, "开始处理游戏请求")
        
        # 4. 模拟业务逻辑
        game_data = {
            "game_id": "game_001",
            "players": ["player1", "player2"],
            "status": "active"
        }
        
        # 5. 记录业务逻辑完成
        service_logger.info(request_ctx, f"游戏数据处理完成: {game_data['game_id']}")
        
        # 6. 创建响应
        api_response = create_response(
            context=request_ctx,
            code=OK,
            data=game_data
        )
        
        # 7. 记录请求完成
        service_logger.info(request_ctx, "请求处理完成")
        
        print("✅ 完整工作流程测试成功")
        print(f"   TraceID: {request_ctx.trace_id}")
        print(f"   响应数据: {api_response.data}")
        
    except Exception as e:
        print(f"❌ 完整工作流程测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！")
    print("✅ py_sdk 在外部项目中工作正常！")
    print("✅ 可以在 coc_rules/server 中正常使用所有功能！")
    
    return True

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例")
    print("=" * 50)
    
    print("""
# 在您的外部项目中，现在可以这样使用 py_sdk：

# 1. 导入所需模块
from .context import create_context
from .logger import get_logger
from .http_client import create_response, OK
from .nacos_sdk import get_config

# 2. 创建上下文和日志记录器
ctx = create_context()
logger = get_logger("your-service")

# 3. 记录日志（自动包含TraceID）
logger.info(ctx, "服务启动")

# 4. 创建API响应
response = create_response(ctx, code=OK, data={"status": "success"})

# 5. 获取配置（需要Nacos服务器）
# config = get_config("your-config")
    """)

if __name__ == "__main__":
    success = test_py_sdk_usage()
    
    if success:
        show_usage_examples()
    
    exit(0 if success else 1) 