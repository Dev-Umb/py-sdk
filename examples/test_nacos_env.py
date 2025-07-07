#!/usr/bin/env python3
"""
简单测试Nacos环境变量配置功能
"""

import os
import sys
sys.path.insert(0, '..')

from nacos_sdk.client import NacosClient, init_nacos_client

def test_env_vars():
    """测试环境变量配置"""
    print("=== 测试环境变量配置 ===")
    
    # 清除所有环境变量
    env_vars = ['NACOS_ADDRESS', 'NACOS_NAMESPACE', 'NACOS_USERNAME', 'NACOS_PASSWORD']
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    
    # 测试1: 默认配置
    print("\n1. 测试默认配置:")
    client = NacosClient()
    print(f"   服务器地址: {client.server_addresses}")
    print(f"   命名空间: '{client.namespace}'")
    print(f"   用户名: {client.username}")
    print(f"   密码: {client.password}")
    
    # 测试2: 环境变量配置
    print("\n2. 测试环境变量配置:")
    os.environ['NACOS_ADDRESS'] = 'test1.example.com:8848,test2.example.com:8848'
    os.environ['NACOS_NAMESPACE'] = 'test-env'
    os.environ['NACOS_USERNAME'] = 'test-user'
    os.environ['NACOS_PASSWORD'] = 'test-pass'
    
    client = NacosClient()
    print(f"   服务器地址: {client.server_addresses}")
    print(f"   命名空间: '{client.namespace}'")
    print(f"   用户名: {client.username}")
    print(f"   密码: {client.password}")
    
    # 测试3: 参数覆盖环境变量
    print("\n3. 测试参数覆盖环境变量:")
    client = NacosClient(
        server_addresses="param.example.com:8848",
        namespace="param-ns",
        username="param-user",
        password="param-pass"
    )
    print(f"   服务器地址: {client.server_addresses}")
    print(f"   命名空间: '{client.namespace}'")
    print(f"   用户名: {client.username}")
    print(f"   密码: {client.password}")
    
    # 测试4: 部分参数覆盖
    print("\n4. 测试部分参数覆盖:")
    client = NacosClient(
        server_addresses="partial.example.com:8848",
        # namespace, username, password 从环境变量读取
    )
    print(f"   服务器地址: {client.server_addresses}")
    print(f"   命名空间: '{client.namespace}'")
    print(f"   用户名: {client.username}")
    print(f"   密码: {client.password}")
    
    print("\n✅ 所有测试完成!")

if __name__ == "__main__":
    test_env_vars() 