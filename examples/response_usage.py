"""
响应创建使用示例

展示新的简化 create_response API：
- context: 上下文对象（必需）
- code: 业务状态码（可选，默认为 OK）
- data: 响应数据（可选）

message 会自动从 code 中获取
"""

from context.manager import create_context
from http_client.response import create_response
from http_client.code import (
    OK, ROOM_NOT_FOUND, INVALID_PARAMS, 
    INTERNAL_SERVER_ERROR, UNAUTHORIZED
)


def demo_basic_responses():
    """演示基本响应创建"""
    print("=== 基本响应创建示例 ===")
    
    # 创建上下文
    ctx = create_context()
    print(f"TraceID: {ctx.trace_id}")
    
    # 1. 最简单的成功响应（默认使用 OK 状态码）
    response1 = create_response(ctx)
    print("\n1. 默认成功响应:")
    print(response1.to_json())
    
    # 2. 带数据的成功响应
    response2 = create_response(ctx, data={"id": 1, "name": "测试房间"})
    print("\n2. 带数据的成功响应:")
    print(response2.to_json())
    
    # 3. 指定状态码的成功响应
    response3 = create_response(ctx, code=OK, data={"result": "操作成功"})
    print("\n3. 指定状态码的成功响应:")
    print(response3.to_json())
    
    # 4. 错误响应（自动使用 code 的 message）
    response4 = create_response(ctx, code=ROOM_NOT_FOUND)
    print("\n4. 错误响应:")
    print(response4.to_json())
    
    # 5. 带错误数据的响应
    response5 = create_response(
        ctx, 
        code=INVALID_PARAMS, 
        data={"field": "room_id", "reason": "不能为空"}
    )
    print("\n5. 带错误数据的响应:")
    print(response5.to_json())


def demo_business_scenarios():
    """演示业务场景"""
    print("\n=== 业务场景示例 ===")
    
    ctx = create_context()
    
    # 用户登录成功
    user_data = {
        "user_id": 12345,
        "username": "testuser",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600
    }
    login_response = create_response(ctx, data=user_data)
    print("\n用户登录成功:")
    print(login_response.to_json())
    
    # 权限不足
    auth_error = create_response(ctx, code=UNAUTHORIZED)
    print("\n权限不足:")
    print(auth_error.to_json())
    
    # 服务器内部错误（带调试信息）
    server_error = create_response(
        ctx, 
        code=INTERNAL_SERVER_ERROR,
        data={"debug_info": "Database connection timeout"}
    )
    print("\n服务器内部错误:")
    print(server_error.to_json())


def demo_paginated_data():
    """演示分页数据响应"""
    print("\n=== 分页数据示例 ===")
    
    ctx = create_context()
    
    # 模拟房间列表数据
    rooms = [
        {"id": 1, "name": "会议室A", "capacity": 10},
        {"id": 2, "name": "会议室B", "capacity": 20},
        {"id": 3, "name": "会议室C", "capacity": 15}
    ]
    
    # 分页信息
    total = 100
    page = 1
    page_size = 3
    total_pages = (total + page_size - 1) // page_size
    
    # 构造分页响应数据
    paginated_data = {
        "items": rooms,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    # 创建分页响应
    response = create_response(ctx, data=paginated_data)
    print("分页数据响应:")
    print(response.to_json())


def demo_api_integration():
    """演示 API 集成示例"""
    print("\n=== API 集成示例 ===")
    
    def get_room(room_id: int):
        """获取房间信息的 API"""
        ctx = create_context()
        
        # 模拟业务逻辑
        if room_id <= 0:
            return create_response(
                ctx, 
                code=INVALID_PARAMS,
                data={"field": "room_id", "message": "房间ID必须大于0"}
            )
        
        if room_id == 999:
            return create_response(ctx, code=ROOM_NOT_FOUND)
        
        # 模拟成功获取房间信息
        room_data = {
            "id": room_id,
            "name": f"会议室{room_id}",
            "capacity": 20,
            "status": "available"
        }
        
        return create_response(ctx, data=room_data)
    
    # 测试不同场景
    print("1. 正常获取房间:")
    response1 = get_room(1)
    print(response1.to_json())
    
    print("\n2. 参数错误:")
    response2 = get_room(-1)
    print(response2.to_json())
    
    print("\n3. 房间不存在:")
    response3 = get_room(999)
    print(response3.to_json())


if __name__ == "__main__":
    demo_basic_responses()
    demo_business_scenarios()
    demo_paginated_data()
    demo_api_integration() 