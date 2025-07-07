#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准包使用示例

演示如何在其他项目中使用 py-sdk 包的正确方式。
这个示例展示了标准化的导入和使用方法。
"""

import os
import sys

# 设置环境变量（实际使用时可以通过 .env 文件或系统环境变量设置）
os.environ.setdefault('NACOS_ADDRESS', '127.0.0.1:8848')
os.environ.setdefault('NACOS_NAMESPACE', 'dev')

def main():
    """主函数 - 演示标准包使用方式"""
    print("🎯 py-sdk 标准包使用示例")
    print("=" * 50)
    
    # 方式1: 从各模块导入（推荐）
    print("\n📦 方式1: 从各模块导入")
    try:
        from context import create_context
        from logger import get_logger
        from http_client import create_response, OK
        
        # 创建上下文
        ctx = create_context()
        print(f"✅ TraceID: {ctx.trace_id}")
        
        # 获取日志记录器
        logger = get_logger("package-example")
        logger.info(ctx, "使用模块导入成功")
        
        # 创建响应
        response = create_response(ctx, code=OK, data={"message": "模块导入成功"})
        print(f"✅ 响应: {response.to_json()}")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("💡 请确保已正确安装 py-sdk 包")
    
    # 方式2: 导入整个模块
    print("\n📦 方式2: 导入整个模块")
    try:
        import context
        import logger
        import http_client
        
        # 使用模块名访问
        ctx = context.create_context()
        log = logger.get_logger("module-example")
        log.info(ctx, "使用模块名导入成功")
        
        response = http_client.create_response(ctx, code=http_client.OK, data={"message": "模块名导入成功"})
        print(f"✅ 模块响应: {response.to_json()}")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
    
    # 方式3: 完整功能演示
    print("\n📦 方式3: 完整功能演示")
    try:
        # 导入所有需要的模块
        from context import create_context
        from logger import get_logger, init_logger_manager
        from http_client import create_response, BusinessCode, HttpClient
        from nacos_sdk import registerNacos, get_config
        
        # 1. 初始化日志管理器
        init_logger_manager(
            config={"handlers": {"console": {"enabled": True}}},
            service_name="complete-example"
        )
        
        # 2. 创建上下文
        ctx = create_context()
        logger = get_logger("complete-example")
        
        # 3. 记录日志
        logger.info(ctx, "完整功能演示开始", extra={
            "version": "1.0.0",
            "mode": "package"
        })
        
        # 4. 创建 HTTP 客户端
        http_client = HttpClient("https://api.example.com")
        
        # 5. 创建标准响应
        success_response = create_response(
            ctx, 
            code=BusinessCode.OK, 
            data={
                "sdk_version": "1.0.0",
                "features": ["logging", "http", "context", "nacos_sdk"],
                "status": "ready"
            }
        )
        
        print(f"✅ 完整功能演示成功")
        print(f"📊 响应数据: {success_response.to_json()}")
        
        logger.info(ctx, "完整功能演示完成", extra={
            "response_code": success_response.code,
            "trace_id": ctx.trace_id
        })
        
    except ImportError as e:
        print(f"❌ 完整功能导入失败: {e}")
    except Exception as e:
        print(f"❌ 完整功能演示失败: {e}")

def demonstrate_web_integration():
    """演示 Web 框架集成"""
    print("\n🌐 Web 框架集成示例")
    print("-" * 30)
    
    # FastAPI 集成示例
    try:
        from http_client import create_fastapi_middleware
        print("✅ FastAPI 中间件可用")
        
        # 示例代码（不实际运行）
        middleware_code = '''
        from fastapi import FastAPI
        from http_client import create_fastapi_middleware
        
        app = FastAPI()
        app.add_middleware(create_fastapi_middleware())
        
        @app.get("/")
        async def root():
            from context import get_current_context
            from logger import get_logger
            ctx = get_current_context()
            logger = get_logger("api")
            logger.info(ctx, "API 请求处理")
            return {"message": "Hello World", "trace_id": ctx.trace_id}
        '''
        print("💡 FastAPI 集成代码示例：")
        print(middleware_code)
        
    except ImportError:
        print("❌ FastAPI 中间件不可用（需要安装 py-sdk[web]）")

def demonstrate_async_usage():
    """演示异步使用方式"""
    print("\n🔄 异步使用示例")
    print("-" * 30)
    
    import asyncio
    
    async def async_task():
        """异步任务示例"""
        try:
            from context import create_context
            from logger import get_logger
            
            # 在异步环境中使用
            ctx = create_context()
            logger = get_logger("async-task")
            
            logger.info(ctx, "异步任务开始")
            
            # 模拟异步操作
            await asyncio.sleep(0.1)
            
            logger.info(ctx, "异步任务完成", extra={
                "task_type": "demo",
                "duration": 0.1
            })
            
            print(f"✅ 异步任务完成，TraceID: {ctx.trace_id}")
            
        except Exception as e:
            print(f"❌ 异步任务失败: {e}")
    
    # 运行异步任务
    try:
        asyncio.run(async_task())
    except Exception as e:
        print(f"❌ 异步示例失败: {e}")

if __name__ == "__main__":
    try:
        main()
        demonstrate_web_integration()
        demonstrate_async_usage()
        
        print("\n" + "=" * 50)
        print("🎉 所有示例完成！")
        print("💡 提示：")
        print("   - 推荐使用模块导入方式: from context import ...")
        print("   - 支持异步安全的上下文传递")
        print("   - 提供完整的 Web 框架集成")
        print("   - 查看更多示例: examples/ 目录")
        
    except KeyboardInterrupt:
        print("\n\n👋 示例被用户中断")
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        sys.exit(1) 