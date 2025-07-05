"""
内网 Nacos 连接示例

展示如何连接到内网 Nacos 服务器并使用完整的 py-sdk 功能。
"""

import os
import sys
import time
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, '.')

from context.manager import create_context, set_context
from logger import init_logger_manager, get_logger
from nacos_sdk.client import NacosClient
from nacos_sdk.api import get_config


def setup_nacos_environment():
    """设置 Nacos 环境变量"""
    print("=== 设置 Nacos 连接配置 ===")
    
    # 设置内网 Nacos 地址
    os.environ['NACOS_ADDRESS'] = '10.15.101.239:8848'
    os.environ['NACOS_NAMESPACE'] = ''  # 使用默认命名空间
    
    # 如果有认证，可以设置用户名密码（当前无需认证）
    # os.environ['NACOS_USERNAME'] = 'nacos'
    # os.environ['NACOS_PASSWORD'] = 'nacos'
    
    print(f"Nacos 地址: {os.environ['NACOS_ADDRESS']}")
    print(f"命名空间: {os.environ.get('NACOS_NAMESPACE', '默认')}")
    print("认证: 无需认证")


def test_nacos_connection():
    """测试 Nacos 连接"""
    print("\n=== 测试 Nacos 连接 ===")
    
    try:
        # 创建 Nacos 客户端
        client = NacosClient()
        
        # 测试连接
        print("正在连接 Nacos 服务器...")
        
        # 尝试获取一个配置（即使不存在也能测试连接）
        test_config = get_config("test.config")
        print("✅ Nacos 连接成功")
        
        if test_config:
            print(f"获取到测试配置: {test_config[:100]}...")
        else:
            print("📝 未找到测试配置（这是正常的）")
            
        return True
        
    except Exception as e:
        print(f"❌ Nacos 连接失败: {str(e)}")
        return False


def upload_sample_configs():
    """上传示例配置到 Nacos"""
    print("\n=== 上传示例配置 ===")
    
    try:
        client = NacosClient()
        
        # 1. 上传 logger 配置
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
                    "filename": "app.log",
                    "max_bytes": 10485760,
                    "backup_count": 5
                },
                "tls": {
                    "enabled": True,
                    "level": "INFO"
                }
            }
        }
        
        import json
        client.publish_config(
            data_id="logger.json",
            content=json.dumps(logger_config, indent=2, ensure_ascii=False),
            group="DEFAULT_GROUP"
        )
        print("✅ logger.json 配置上传成功")
        
        # 2. 上传 TLS 日志配置
        tls_config = {
            "VOLCENGINE_ENDPOINT": "https://tls-cn-beijing.volces.com",
            "VOLCENGINE_ACCESS_KEY_ID": "your-access-key-id-here",
            "VOLCENGINE_ACCESS_KEY_SECRET": "your-access-key-secret-here",
            "VOLCENGINE_TOKEN": "",
            "VOLCENGINE_REGION": "cn-beijing"
        }
        
        client.publish_config(
            data_id="tls.log.config",
            content=json.dumps(tls_config, indent=2, ensure_ascii=False),
            group="DEFAULT_GROUP"
        )
        print("✅ tls.log.config 配置上传成功")
        
        # 3. 上传服务配置
        services_config = {
            "services": [
                {
                    "name": "demo-service",
                    "port": 8080,
                    "service_type": "http",
                    "protocols": ["http"],
                    "metadata": {
                        "service": "demo",
                        "version": "1.0.0"
                    },
                    "cluster": "DEFAULT",
                    "group": "DEFAULT_GROUP"
                }
            ]
        }
        
        client.publish_config(
            data_id="services.json",
            content=json.dumps(services_config, indent=2, ensure_ascii=False),
            group="DEFAULT_GROUP"
        )
        print("✅ services.json 配置上传成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置上传失败: {str(e)}")
        return False


def test_config_retrieval():
    """测试配置获取"""
    print("\n=== 测试配置获取 ===")
    
    try:
        # 获取 logger 配置
        logger_config = get_config("logger.json")
        if logger_config:
            print("✅ 成功获取 logger.json 配置")
            print(f"配置内容预览: {logger_config[:100]}...")
        else:
            print("❌ 未获取到 logger.json 配置")
        
        # 获取 TLS 配置
        tls_config = get_config("tls.log.config")
        if tls_config:
            print("✅ 成功获取 tls.log.config 配置")
            print("配置内容: [已隐藏敏感信息]")
        else:
            print("❌ 未获取到 tls.log.config 配置")
        
        # 获取服务配置
        services_config = get_config("services.json")
        if services_config:
            print("✅ 成功获取 services.json 配置")
            print(f"配置内容预览: {services_config[:100]}...")
        else:
            print("❌ 未获取到 services.json 配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置获取失败: {str(e)}")
        return False


def test_logger_with_nacos():
    """测试从 Nacos 获取配置并初始化 Logger"""
    print("\n=== 测试 Logger 与 Nacos 集成 ===")
    
    try:
        # 从 Nacos 获取 logger 配置
        logger_config_str = get_config("logger.json")
        if not logger_config_str:
            print("⚠️  未获取到 logger 配置，使用默认配置")
            logger_config = {
                "handlers": {
                    "console": {"enabled": True}
                }
            }
        else:
            import json
            logger_config = json.loads(logger_config_str)
            print("✅ 成功从 Nacos 获取 logger 配置")
        
        # 初始化 logger（使用示例 TopicID）
        init_logger_manager(
            config=logger_config,
            topic_id="demo-service-logs",
            service_name="demo-service"
        )
        print("✅ Logger 初始化成功")
        
        # 测试日志记录
        logger = get_logger("nacos-demo")
        ctx = create_context()
        set_context(ctx)
        
        print(f"TraceID: {ctx.trace_id}")
        
        # 记录各种日志
        logger.info(ctx, "Nacos 集成测试开始")
        logger.info(ctx, "用户操作", extra={
            "user_id": 12345,
            "action": "test_nacos_integration",
            "nacos_server": "10.15.101.239:8848"
        })
        
        logger.warning(ctx, "这是一个警告日志", extra={
            "warning_type": "test",
            "severity": "low"
        })
        
        # 模拟业务操作
        for i in range(3):
            logger.info(ctx, f"处理任务 {i+1}", extra={
                "task_id": f"task-{i+1}",
                "progress": f"{(i+1)*33}%"
            })
            time.sleep(0.1)
        
        logger.info(ctx, "Nacos 集成测试完成")
        print("✅ 日志记录测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ Logger 测试失败: {str(e)}")
        return False


def demo_dynamic_config_update():
    """演示动态配置更新"""
    print("\n=== 演示动态配置更新 ===")
    
    try:
        client = NacosClient()
        
        # 创建一个测试配置
        test_config = {
            "app_name": "demo-service",
            "version": "1.0.0",
            "debug": True,
            "max_connections": 100
        }
        
        import json
        client.publish_config(
            data_id="app.config",
            content=json.dumps(test_config, indent=2),
            group="DEFAULT_GROUP"
        )
        print("✅ 发布测试配置")
        
        # 获取配置
        config_content = get_config("app.config")
        if config_content:
            config_data = json.loads(config_content)
            print(f"✅ 获取配置: {config_data}")
        
        # 更新配置
        test_config["version"] = "1.0.1"
        test_config["max_connections"] = 200
        
        client.publish_config(
            data_id="app.config",
            content=json.dumps(test_config, indent=2),
            group="DEFAULT_GROUP"
        )
        print("✅ 更新配置")
        
        # 再次获取配置
        time.sleep(0.5)  # 等待配置更新
        updated_config = get_config("app.config")
        if updated_config:
            updated_data = json.loads(updated_config)
            print(f"✅ 获取更新后配置: {updated_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ 动态配置更新测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("内网 Nacos 连接与集成测试")
    print("=" * 50)
    
    # 1. 设置环境
    setup_nacos_environment()
    
    # 2. 测试连接
    if not test_nacos_connection():
        print("❌ Nacos 连接失败，请检查网络和地址配置")
        return
    
    # 3. 上传配置（可选）
    print("\n是否要上传示例配置到 Nacos？(y/n): ", end="")
    upload_choice = input().lower().strip()
    if upload_choice in ['y', 'yes']:
        upload_sample_configs()
    
    # 4. 测试配置获取
    test_config_retrieval()
    
    # 5. 测试 Logger 集成
    test_logger_with_nacos()
    
    # 6. 演示动态配置
    demo_dynamic_config_update()
    
    print("\n" + "=" * 50)
    print("✅ 内网 Nacos 集成测试完成！")
    print("\n使用说明：")
    print("1. 确保 Nacos 服务器 10.15.101.239:8848 可访问")
    print("2. 根据需要在 Nacos 控制台中配置相应的 DataID")
    print("3. 在实际项目中设置正确的火山引擎 TLS 认证信息")
    print("4. 每个服务使用不同的 TopicID")


if __name__ == "__main__":
    main() 