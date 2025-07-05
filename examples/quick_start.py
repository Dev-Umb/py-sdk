"""
快速启动示例

最简单的 py-sdk 使用方式，连接内网 Nacos。
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, '.')

# 设置内网 Nacos 地址
os.environ['NACOS_ADDRESS'] = '10.15.101.239:8848'
os.environ['NACOS_NAMESPACE'] = ''

# 导入 py-sdk
from context.manager import create_context
from logger import init_logger_manager, get_logger
from http_client.response import create_response
from http_client.code import OK, ROOM_NOT_FOUND


def main():
    """快速启动示例"""
    print("🚀 py-sdk 快速启动")
    print(f"📡 Nacos: {os.environ['NACOS_ADDRESS']}")
    print()
    
    # 1. 初始化 Logger（使用最简配置）
    init_logger_manager(
        config={"handlers": {"console": {"enabled": True}}},
        topic_id="2a6a07f0-8490-4a72-9a41-e5f25c578751",
        service_name="quick-start"
    )
    
    # 2. 创建上下文
    ctx = create_context()
    print(f"📝 TraceID: {ctx.trace_id}")
    
    # 3. 获取 Logger
    logger = get_logger("quick-start")
    
    # 4. 记录日志
    logger.info(ctx, "快速启动测试开始")
    logger.info(ctx, "用户操作", extra={"action": "test", "user_id": 123})
    
    # 5. 创建响应
    success_response = create_response(ctx, data={"message": "快速启动成功！"})
    print(f"✅ 成功响应: {success_response.to_json()}")
    
    error_response = create_response(ctx, code=ROOM_NOT_FOUND)
    print(f"❌ 错误响应: {error_response.to_json()}")
    
    logger.info(ctx, "快速启动测试完成")
    print()
    print("🎉 快速启动完成！")
    print("💡 接下来运行：")
    print("   - python examples/basic_usage.py          # 完整功能示例")
    print("   - python examples/fastapi_example.py      # FastAPI 集成")
    print("   - python examples/nacos_connection_example.py  # Nacos 连接测试")


if __name__ == "__main__":
    main() 