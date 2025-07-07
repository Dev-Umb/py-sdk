#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文管理模块示例

演示如何使用 context 模块进行上下文管理和 TraceID 传递。
"""

import asyncio
import time
from context import (
    create_context, 
    get_current_context, 
    get_trace_id,
    create_context_from_request
)


def main():
    """主函数"""
    print("🔗 上下文管理模块示例")
    print("=" * 50)
    
    # 1. 基础使用
    print("\n📋 1. 基础使用")
    basic_usage()
    
    # 2. 自定义 TraceID
    print("\n📋 2. 自定义 TraceID")
    custom_trace_id()
    
    # 3. 业务逻辑处理
    print("\n📋 3. 业务逻辑处理")
    business_logic_example()
    
    # 4. 异步环境
    print("\n📋 4. 异步环境")
    asyncio.run(async_example())
    
    # 5. HTTP 请求模拟
    print("\n📋 5. HTTP 请求模拟")
    http_request_example()
    
    print("\n" + "=" * 50)
    print("✅ 上下文管理示例完成！")


def basic_usage():
    """基础使用示例"""
    print("创建上下文（自动生成 TraceID）...")
    
    # 创建上下文
    ctx = create_context()
    print(f"✓ 上下文创建成功: {ctx}")
    print(f"  TraceID: {ctx.trace_id}")
    print(f"  创建时间: {ctx.created_at}")
    
    # 获取当前 TraceID
    trace_id = get_trace_id()
    print(f"✓ 当前 TraceID: {trace_id}")
    
    # 获取当前上下文
    current_ctx = get_current_context()
    print(f"✓ 当前上下文: {current_ctx}")


def custom_trace_id():
    """自定义 TraceID 示例"""
    print("使用自定义 TraceID...")
    
    # 使用自定义 TraceID
    custom_id = "my-custom-trace-id-12345"
    ctx = create_context(trace_id=custom_id)
    
    print(f"✓ 自定义 TraceID: {ctx.trace_id}")
    print(f"✓ 验证是否匹配: {ctx.trace_id == custom_id}")


def business_logic_example():
    """业务逻辑处理示例"""
    print("模拟业务逻辑处理...")
    
    # 创建请求上下文
    ctx = create_context()
    print(f"✓ 请求开始，TraceID: {ctx.trace_id}")
    
    # 模拟业务处理步骤
    process_step_1()
    process_step_2()
    process_step_3()
    
    print(f"✓ 请求完成，TraceID: {get_trace_id()}")


def process_step_1():
    """业务处理步骤1"""
    trace_id = get_trace_id()
    print(f"  步骤1: 数据验证 [TraceID: {trace_id}]")
    time.sleep(0.1)  # 模拟处理时间


def process_step_2():
    """业务处理步骤2"""
    trace_id = get_trace_id()
    print(f"  步骤2: 业务逻辑处理 [TraceID: {trace_id}]")
    time.sleep(0.1)  # 模拟处理时间


def process_step_3():
    """业务处理步骤3"""
    trace_id = get_trace_id()
    print(f"  步骤3: 结果返回 [TraceID: {trace_id}]")
    time.sleep(0.1)  # 模拟处理时间


async def async_example():
    """异步环境示例"""
    print("异步环境中的上下文管理...")
    
    # 创建上下文
    ctx = create_context()
    print(f"✓ 主协程 TraceID: {ctx.trace_id}")
    
    # 启动多个异步任务
    tasks = [
        async_task("任务A"),
        async_task("任务B"),
        async_task("任务C")
    ]
    
    await asyncio.gather(*tasks)
    
    # 验证主协程的上下文仍然存在
    current_trace_id = get_trace_id()
    print(f"✓ 主协程结束，TraceID: {current_trace_id}")


async def async_task(task_name):
    """异步任务"""
    # 在异步任务中获取上下文
    trace_id = get_trace_id()
    print(f"  {task_name} 开始执行 [TraceID: {trace_id}]")
    
    # 模拟异步操作
    await asyncio.sleep(0.1)
    
    # 验证上下文仍然存在
    final_trace_id = get_trace_id()
    print(f"  {task_name} 执行完成 [TraceID: {final_trace_id}]")


def http_request_example():
    """HTTP 请求模拟示例"""
    print("模拟 HTTP 请求处理...")
    
    # 模拟不同类型的请求
    requests = [
        {"headers": {"X-Trace-Id": "external-trace-123"}},
        {"headers": {"x-trace-id": "external-trace-456"}},
        {"headers": {}},  # 没有 TraceID 的请求
    ]
    
    for i, request in enumerate(requests, 1):
        print(f"\n  请求 {i}:")
        handle_http_request(request)


def handle_http_request(request):
    """处理 HTTP 请求"""
    # 从请求创建上下文
    ctx = create_context_from_request(MockRequest(request))
    
    print(f"    请求处理开始，TraceID: {ctx.trace_id}")
    
    # 模拟请求处理
    process_http_business_logic()
    
    print(f"    请求处理完成，TraceID: {get_trace_id()}")


def process_http_business_logic():
    """处理 HTTP 业务逻辑"""
    trace_id = get_trace_id()
    print(f"    执行业务逻辑 [TraceID: {trace_id}]")


class MockRequest:
    """模拟请求对象"""
    
    def __init__(self, request_data):
        self.headers = request_data.get("headers", {})


if __name__ == "__main__":
    main() 