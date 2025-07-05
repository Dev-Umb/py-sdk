#!/usr/bin/env python3
"""
Nacos环境变量配置示例

这个示例展示了如何使用环境变量来配置Nacos客户端，
以及如何在不同的环境中使用不同的配置。
"""

import os
import time
from nacos_sdk import registerNacos, unregisterNacos, init_nacos_client

def example_with_env_vars():
    """使用环境变量配置的示例"""
    print("=== 使用环境变量配置Nacos ===")
    
    # 设置环境变量（在实际应用中，这些通常在启动脚本或容器配置中设置）
    os.environ['NACOS_SERVER_ADDRESSES'] = '192.168.1.100:8848,192.168.1.101:8848'
    os.environ['NACOS_NAMESPACE'] = 'dev'
    os.environ['NACOS_USERNAME'] = 'nacos'
    os.environ['NACOS_PASSWORD'] = 'nacos'
    
    # 不需要传递任何参数，会自动从环境变量读取
    success = registerNacos(
        service_name="user-service",
        port=8080,
        metadata={
            "version": "1.0.0",
            "env": "dev"
        }
    )
    
    if success:
        print("✅ 服务注册成功（使用环境变量配置）")
        print(f"   服务器地址: {os.environ['NACOS_SERVER_ADDRESSES']}")
        print(f"   命名空间: {os.environ['NACOS_NAMESPACE']}")
        
        # 等待一段时间
        time.sleep(5)
        
        # 注销服务
        unregisterNacos("user-service", 8080)
        print("✅ 服务注销成功")
    else:
        print("❌ 服务注册失败")

def example_with_mixed_config():
    """混合配置示例：部分使用环境变量，部分使用参数"""
    print("\n=== 混合配置示例 ===")
    
    # 设置部分环境变量
    os.environ['NACOS_SERVER_ADDRESSES'] = '127.0.0.1:8848'
    os.environ['NACOS_NAMESPACE'] = 'test'
    # 用户名和密码通过参数传递
    
    success = registerNacos(
        service_name="order-service",
        port=8081,
        # server_addresses 和 namespace 从环境变量读取
        # 但可以通过参数覆盖
        username="admin",  # 通过参数传递
        password="admin123",  # 通过参数传递
        metadata={
            "version": "2.0.0",
            "env": "test"
        }
    )
    
    if success:
        print("✅ 服务注册成功（混合配置）")
        time.sleep(5)
        unregisterNacos("order-service", 8081)
        print("✅ 服务注销成功")
    else:
        print("❌ 服务注册失败")

def example_with_default_config():
    """使用默认配置的示例"""
    print("\n=== 使用默认配置示例 ===")
    
    # 清除环境变量，使用默认配置
    env_vars_to_clear = ['NACOS_SERVER_ADDRESSES', 'NACOS_NAMESPACE', 'NACOS_USERNAME', 'NACOS_PASSWORD']
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    # 不传递任何参数，使用默认配置
    success = registerNacos(
        service_name="payment-service",
        port=8082,
        metadata={
            "version": "1.0.0",
            "env": "local"
        }
    )
    
    if success:
        print("✅ 服务注册成功（使用默认配置 127.0.0.1:8848）")
        time.sleep(5)
        unregisterNacos("payment-service", 8082)
        print("✅ 服务注销成功")
    else:
        print("❌ 服务注册失败")

def example_direct_client_usage():
    """直接使用客户端的示例"""
    print("\n=== 直接使用客户端示例 ===")
    
    # 设置环境变量
    os.environ['NACOS_SERVER_ADDRESSES'] = '127.0.0.1:8848'
    os.environ['NACOS_NAMESPACE'] = 'prod'
    
    # 初始化客户端（从环境变量读取配置）
    client = init_nacos_client()
    
    # 注册服务
    success = client.register_service(
        service_name="notification-service",
        ip="192.168.1.10",
        port=8083,
        metadata={
            "version": "1.0.0",
            "env": "prod"
        }
    )
    
    if success:
        print("✅ 服务注册成功（直接使用客户端）")
        
        # 获取服务实例
        instances = client.get_service_instances("notification-service")
        print(f"   发现 {len(instances)} 个服务实例")
        
        time.sleep(5)
        
        # 注销服务
        client.deregister_service("notification-service", "192.168.1.10", 8083)
        print("✅ 服务注销成功")
    else:
        print("❌ 服务注册失败")

def show_env_priority():
    """展示环境变量优先级"""
    print("\n=== 环境变量优先级示例 ===")
    print("优先级：参数 > 环境变量 > 默认值")
    
    # 设置环境变量
    os.environ['NACOS_SERVER_ADDRESSES'] = '192.168.1.100:8848'
    os.environ['NACOS_NAMESPACE'] = 'env-namespace'
    
    # 通过参数覆盖环境变量
    success = registerNacos(
        service_name="config-service",
        port=8084,
        server_addresses="127.0.0.1:8848",  # 参数覆盖环境变量
        namespace="param-namespace",        # 参数覆盖环境变量
        metadata={
            "version": "1.0.0",
            "priority": "param-over-env"
        }
    )
    
    if success:
        print("✅ 服务注册成功（参数优先级高于环境变量）")
        print("   实际使用: 127.0.0.1:8848, namespace=param-namespace")
        time.sleep(5)
        unregisterNacos("config-service", 8084)
        print("✅ 服务注销成功")
    else:
        print("❌ 服务注册失败")

if __name__ == "__main__":
    print("Nacos环境变量配置示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        example_with_env_vars()
        example_with_mixed_config()
        example_with_default_config()
        example_direct_client_usage()
        show_env_priority()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {str(e)}")
        import traceback
        traceback.print_exc() 