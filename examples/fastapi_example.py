"""
FastAPI 集成示例

展示如何在 FastAPI 应用中集成 py-sdk 的各种功能，
包括连接内网 Nacos 和使用完整的日志功能。
"""

import os
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# 导入 py-sdk 模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context.manager import create_context, set_context, get_current_context
from logger import init_logger_manager, get_logger
from http_client.response import create_response
from http_client.code import ROOM_NOT_FOUND, INVALID_PARAMS, UNAUTHORIZED, INTERNAL_SERVER_ERROR
from http_client.middleware import create_fastapi_middleware
from nacos.api import get_config
from nacos.client import NacosClient


# 数据模型
class User(BaseModel):
    name: str
    email: Optional[str] = None
    age: Optional[int] = None


class Room(BaseModel):
    name: str
    capacity: int
    description: Optional[str] = None


def setup_nacos_environment():
    """设置 Nacos 环境变量"""
    # 设置内网 Nacos 地址
    os.environ['NACOS_ADDRESS'] = '10.15.101.239:8848'
    os.environ['NACOS_NAMESPACE'] = ''  # 使用默认命名空间
    print(f"✅ 配置 Nacos 地址: {os.environ['NACOS_ADDRESS']}")


def init_logger_from_nacos():
    """从 Nacos 获取配置并初始化 Logger"""
    try:
        # 从 Nacos 获取 logger 配置
        logger_config_str = get_config("logger.json")
        if logger_config_str:
            logger_config = json.loads(logger_config_str)
            print("✅ 从 Nacos 获取 logger 配置成功")
        else:
            # 使用默认配置
            logger_config = {
                "level": "INFO",
                "handlers": {
                    "console": {"enabled": True, "level": "INFO"},
                    "file": {"enabled": True, "level": "INFO", "filename": "fastapi-app.log"},
                    "tls": {"enabled": True, "level": "INFO"}
                }
            }
            print("⚠️  未获取到 Nacos logger 配置，使用默认配置")
        
        # 初始化 logger
        init_logger_manager(
            config=logger_config,
            topic_id="fastapi-demo-logs",
            service_name="fastapi-demo"
        )
        print("✅ Logger 初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ Logger 初始化失败: {str(e)}")
        # 使用最简配置作为备用
        init_logger_manager(
            config={"handlers": {"console": {"enabled": True}}},
            topic_id="fastapi-demo-logs",
            service_name="fastapi-demo"
        )
        return False


def register_service_to_nacos():
    """注册服务到 Nacos"""
    try:
        client = NacosClient("10.15.101.239:8848")
        
        # 服务注册信息
        service_info = {
            "service_name": "fastapi-demo",
            "ip": "127.0.0.1",  # 实际部署时应使用真实 IP
            "port": 8000,
            "metadata": {
                "framework": "fastapi",
                "version": "1.0.0",
                "description": "py-sdk FastAPI 演示服务"
            }
        }
        
        # 注册服务
        success = client.add_naming_instance(
            service_name=service_info["service_name"],
            ip=service_info["ip"],
            port=service_info["port"],
            metadata=service_info["metadata"]
        )
        
        if success:
            print("✅ 服务注册到 Nacos 成功")
            return True
        else:
            print("❌ 服务注册到 Nacos 失败")
            return False
            
    except Exception as e:
        print(f"❌ 服务注册异常: {str(e)}")
        return False


# 设置环境和初始化
setup_nacos_environment()
init_logger_from_nacos()

# 创建 FastAPI 应用
app = FastAPI(
    title="py-sdk FastAPI 演示",
    description="展示 py-sdk 在 FastAPI 中的完整使用，包括内网 Nacos 集成",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加 py-sdk 中间件
app.middleware("http")(create_fastapi_middleware())

# 获取日志记录器
logger = get_logger("fastapi-demo")

# 模拟数据存储
users_db = {}
rooms_db = {}
next_user_id = 1
next_room_id = 1


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    ctx = create_context()
    logger.info(ctx, "FastAPI 应用启动", extra={
        "service": "fastapi-demo",
        "nacos_server": "10.15.101.239:8848"
    })
    
    # 注册服务到 Nacos
    register_service_to_nacos()
    
    # 初始化一些示例数据
    global users_db, rooms_db, next_user_id, next_room_id
    users_db[1] = {"id": 1, "name": "张三", "email": "zhangsan@example.com", "age": 25}
    users_db[2] = {"id": 2, "name": "李四", "email": "lisi@example.com", "age": 30}
    next_user_id = 3
    
    rooms_db[1] = {"id": 1, "name": "会议室A", "capacity": 10, "description": "小型会议室"}
    rooms_db[2] = {"id": 2, "name": "会议室B", "capacity": 20, "description": "中型会议室"}
    next_room_id = 3
    
    logger.info(ctx, "示例数据初始化完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    ctx = create_context()
    logger.info(ctx, "FastAPI 应用关闭")


@app.get("/")
async def root():
    """根路径"""
    ctx = get_current_context()
    logger.info(ctx, "访问根路径")
    
    return create_response(
        ctx,
        data={
            "message": "欢迎使用 py-sdk FastAPI 演示",
            "version": "1.0.0",
            "nacos_server": "10.15.101.239:8848",
            "features": [
                "内网 Nacos 集成",
                "自动 TraceID",
                "结构化日志",
                "统一响应格式",
                "业务状态码"
            ]
        }
    ).to_dict()


@app.get("/health")
async def health_check():
    """健康检查"""
    ctx = get_current_context()
    logger.info(ctx, "健康检查")
    
    return create_response(
        ctx,
        data={
            "status": "healthy",
            "service": "fastapi-demo",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    ).to_dict()


# 用户相关 API
@app.get("/users")
async def get_users():
    """获取用户列表"""
    ctx = get_current_context()
    logger.info(ctx, "获取用户列表")
    
    user_list = list(users_db.values())
    
    return create_response(
        ctx,
        data={
            "users": user_list,
            "total": len(user_list)
        }
    ).to_dict()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    ctx = get_current_context()
    logger.info(ctx, f"获取用户信息: {user_id}", extra={"user_id": user_id})
    
    # 参数验证
    if user_id <= 0:
        logger.warning(ctx, f"无效的用户ID: {user_id}", extra={"user_id": user_id})
        return create_response(
            ctx,
            code=INVALID_PARAMS,
            data={"field": "user_id", "message": "用户ID必须大于0"}
        ).to_dict()
    
    # 查找用户
    user = users_db.get(user_id)
    if not user:
        logger.warning(ctx, f"用户不存在: {user_id}", extra={"user_id": user_id})
        return create_response(ctx, code=ROOM_NOT_FOUND).to_dict()
    
    logger.info(ctx, f"成功获取用户信息: {user['name']}", extra={
        "user_id": user_id,
        "user_name": user["name"]
    })
    
    return create_response(ctx, data=user).to_dict()


@app.post("/users")
async def create_user(user: User):
    """创建用户"""
    ctx = get_current_context()
    logger.info(ctx, f"创建用户: {user.name}", extra={"user_name": user.name})
    
    global next_user_id
    
    # 创建新用户
    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age
    }
    
    users_db[next_user_id] = new_user
    next_user_id += 1
    
    logger.info(ctx, f"用户创建成功: {new_user['name']}", extra={
        "user_id": new_user["id"],
        "user_name": new_user["name"]
    })
    
    return create_response(ctx, data=new_user).to_dict()


# 房间相关 API
@app.get("/rooms")
async def get_rooms():
    """获取房间列表"""
    ctx = get_current_context()
    logger.info(ctx, "获取房间列表")
    
    room_list = list(rooms_db.values())
    
    return create_response(
        ctx,
        data={
            "rooms": room_list,
            "total": len(room_list)
        }
    ).to_dict()


@app.get("/rooms/{room_id}")
async def get_room(room_id: int):
    """获取房间信息"""
    ctx = get_current_context()
    logger.info(ctx, f"获取房间信息: {room_id}", extra={"room_id": room_id})
    
    # 参数验证
    if room_id <= 0:
        return create_response(
            ctx,
            code=INVALID_PARAMS,
            data={"field": "room_id", "message": "房间ID必须大于0"}
        ).to_dict()
    
    # 查找房间
    room = rooms_db.get(room_id)
    if not room:
        logger.warning(ctx, f"房间不存在: {room_id}", extra={"room_id": room_id})
        return create_response(ctx, code=ROOM_NOT_FOUND).to_dict()
    
    logger.info(ctx, f"成功获取房间信息: {room['name']}", extra={
        "room_id": room_id,
        "room_name": room["name"]
    })
    
    return create_response(ctx, data=room).to_dict()


@app.post("/rooms")
async def create_room(room: Room):
    """创建房间"""
    ctx = get_current_context()
    logger.info(ctx, f"创建房间: {room.name}", extra={"room_name": room.name})
    
    global next_room_id
    
    # 创建新房间
    new_room = {
        "id": next_room_id,
        "name": room.name,
        "capacity": room.capacity,
        "description": room.description
    }
    
    rooms_db[next_room_id] = new_room
    next_room_id += 1
    
    logger.info(ctx, f"房间创建成功: {new_room['name']}", extra={
        "room_id": new_room["id"],
        "room_name": new_room["name"],
        "capacity": new_room["capacity"]
    })
    
    return create_response(ctx, data=new_room).to_dict()


@app.get("/config")
async def get_nacos_config():
    """获取 Nacos 配置（演示配置获取）"""
    ctx = get_current_context()
    logger.info(ctx, "获取 Nacos 配置")
    
    try:
        # 获取各种配置
        configs = {}
        
        logger_config = get_config("logger.json")
        if logger_config:
            configs["logger"] = "已配置"
        
        tls_config = get_config("tls.log.config")
        if tls_config:
            configs["tls"] = "已配置"
        
        services_config = get_config("services.json")
        if services_config:
            configs["services"] = "已配置"
        
        return create_response(
            ctx,
            data={
                "nacos_server": "10.15.101.239:8848",
                "configs": configs,
                "status": "connected"
            }
        ).to_dict()
        
    except Exception as e:
        logger.error(ctx, f"获取 Nacos 配置失败: {str(e)}")
        return create_response(
            ctx,
            code=INTERNAL_SERVER_ERROR,
            data={"error": "无法连接到 Nacos"}
        ).to_dict()


@app.get("/error")
async def error_example():
    """错误示例"""
    ctx = get_current_context()
    logger.info(ctx, "触发错误示例")
    
    # 故意触发异常
    raise HTTPException(status_code=500, detail="这是一个测试错误")


# 异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    ctx = get_current_context()
    logger.error(ctx, f"HTTP异常: {exc.status_code} - {exc.detail}", extra={
        "status_code": exc.status_code,
        "detail": exc.detail,
        "path": str(request.url.path)
    })
    
    return JSONResponse(
        status_code=200,  # HTTP 状态码始终为 200
        content=create_response(
            ctx,
            code=INTERNAL_SERVER_ERROR,
            data={"http_status": exc.status_code, "detail": exc.detail}
        ).to_dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    ctx = get_current_context()
    logger.exception(ctx, "未处理的异常", extra={
        "exception_type": type(exc).__name__,
        "path": str(request.url.path)
    })
    
    return JSONResponse(
        status_code=200,  # HTTP 状态码始终为 200
        content=create_response(
            ctx,
            code=INTERNAL_SERVER_ERROR,
            data={"error": "服务器内部错误"}
        ).to_dict()
    )


if __name__ == "__main__":
    print("启动 FastAPI 演示应用...")
    print("特性:")
    print("- 内网 Nacos 集成 (10.15.101.239:8848)")
    print("- 自动 TraceID 生成")
    print("- 结构化日志记录")
    print("- 统一响应格式")
    print("- 业务状态码系统")
    print("\n访问 http://localhost:8000/docs 查看 API 文档")
    
    # 启动应用
    uvicorn.run(
        "fastapi_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 