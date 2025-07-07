"""
简化使用示例

展示 py_sdk 最简单的使用方法 - 只需要 TraceID。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context import create_context, get_trace_id
from logger import get_logger

def simple_example():
    """最简单的使用示例"""
    print("=== py_sdk 简化使用示例 ===")
    
    # 1. 创建上下文（自动生成 TraceID）
    ctx = create_context()
    print(f"TraceID: {ctx.trace_id}")
    
    # 2. 获取日志记录器并记录日志
    logger = get_logger("simple-example")
    
    # 3. 记录日志（自动包含 TraceID）
    logger.info(ctx, "这是一条简单的日志")
    logger.info(ctx, "处理业务逻辑", extra={"step": 1})
    logger.info(ctx, "业务处理完成", extra={"result": "success"})
    
    # 4. 也可以直接获取 TraceID
    trace_id = get_trace_id()
    print(f"当前 TraceID: {trace_id}")
    
    print("示例完成！")

def custom_trace_id_example():
    """自定义 TraceID 示例"""
    print("\n=== 自定义 TraceID 示例 ===")
    
    # 使用自定义 TraceID
    ctx = create_context(trace_id="my-custom-trace-123")
    print(f"自定义 TraceID: {ctx.trace_id}")
    
    logger = get_logger("custom-trace")
    logger.info(ctx, "使用自定义 TraceID 的日志")
    
    print("自定义 TraceID 示例完成！")

def multiple_contexts_example():
    """多个上下文示例"""
    print("\n=== 多个上下文示例 ===")
    
    logger = get_logger("multi-context")
    
    # 创建多个不同的上下文
    for i in range(3):
        ctx = create_context()
        logger.info(ctx, f"处理第 {i+1} 个任务", extra={"task_id": i+1})
    
    print("多个上下文示例完成！")

def main():
    """主函数"""
    print("py_sdk 简化版本使用演示")
    print("特点：只需要 TraceID，API 极其简单")
    print("=" * 50)
    
    # 基础示例
    simple_example()
    
    # 自定义 TraceID
    custom_trace_id_example()
    
    # 多个上下文
    multiple_contexts_example()
    
    print("\n" + "=" * 50)
    print("所有示例完成！")
    print("注意：所有日志都会自动包含 TraceID，便于链路追踪。")

if __name__ == "__main__":
    main() 