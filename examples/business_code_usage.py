"""
业务状态码使用示例

展示如何使用新的业务状态码系统，HTTP 响应始终为 200，
业务状态码在响应 body 中体现。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context import create_context, set_context
from http_client.response import create_response
from http_client.code import (
    OK, INTERNAL_SERVER_ERROR, ROOM_NOT_FOUND, UNAUTHORIZED, 
    INVALID_PARAMS, USER_NOT_FOUND
)

def basic_business_code_examples():
    """基础业务状态码示例"""
    print("=== 基础业务状态码示例 ===")
    
    ctx = create_context()
    set_context(ctx)
    
    print(f"TraceID: {ctx.trace_id}")
    print()
    
    # 1. 成功响应（默认使用 OK）
    success_resp = create_response(
        ctx,
        data={"user_id": 123, "username": "张三"}
    )
    
    print("成功响应:")
    print(success_resp.to_json())
    print()
    
    # 2. 房间不存在错误（自动使用 code 的 message）
    room_error = create_response(ctx, code=ROOM_NOT_FOUND)
    
    print("房间不存在错误:")
    print(room_error.to_json())
    print()
    
    # 3. 参数错误（带错误详情）
    param_error = create_response(
        ctx,
        code=INVALID_PARAMS,
        data={"field": "email", "reason": "格式不正确"}
    )
    
    print("参数错误:")
    print(param_error.to_json())
    print()

def advanced_business_scenarios():
    """高级业务场景示例"""
    print("=== 高级业务场景示例 ===")
    
    ctx = create_context()
    
    # 1. 用户认证失败
    auth_error = create_response(ctx, code=UNAUTHORIZED)
    print("认证失败:")
    print(auth_error.to_json())
    print()
    
    # 2. 用户不存在
    user_error = create_response(
        ctx, 
        code=USER_NOT_FOUND,
        data={"user_id": 999}
    )
    print("用户不存在:")
    print(user_error.to_json())
    print()
    
    # 3. 服务器内部错误
    server_error = create_response(
        ctx,
        code=INTERNAL_SERVER_ERROR,
        data={"error_id": "ERR_DB_001", "timestamp": "2023-12-01T10:30:00Z"}
    )
    print("服务器内部错误:")
    print(server_error.to_json())
    print()

def api_simulation():
    """API 模拟示例"""
    print("=== API 模拟示例 ===")
    
    def get_user_info(user_id: int):
        """获取用户信息 API"""
        ctx = create_context()
        
        if user_id <= 0:
            return create_response(
                ctx,
                code=INVALID_PARAMS,
                data={"field": "user_id", "message": "用户ID必须大于0"}
            )
        
        if user_id == 999:
            return create_response(ctx, code=USER_NOT_FOUND)
        
        # 模拟成功获取用户信息
        user_data = {
            "user_id": user_id,
            "username": f"user_{user_id}",
            "email": f"user_{user_id}@example.com",
            "status": "active"
        }
        
        return create_response(ctx, data=user_data)
    
    # 测试不同场景
    print("1. 正常获取用户:")
    response1 = get_user_info(123)
    print(response1.to_json())
    print()
    
    print("2. 参数错误:")
    response2 = get_user_info(-1)
    print(response2.to_json())
    print()
    
    print("3. 用户不存在:")
    response3 = get_user_info(999)
    print(response3.to_json())
    print()

def main():
    """主函数"""
    print("业务状态码系统使用演示")
    print("特点：HTTP 状态码始终为 200，业务状态码在 body 中体现")
    print("新 API：create_response(context, code, data) - 简化参数")
    print("=" * 70)
    
    # 基础示例
    basic_business_code_examples()
    
    # 高级场景
    advanced_business_scenarios()
    
    # API 模拟
    api_simulation()
    
    print("=" * 70)
    print("演示完成！")
    print("关键改进：")
    print("1. code 参数可选，默认为 OK")
    print("2. message 自动从 code 中获取")
    print("3. 只需要三个参数：context、code、data")

if __name__ == "__main__":
    main()