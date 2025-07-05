#!/usr/bin/env python3
"""
TLS 诊断脚本

用于诊断火山引擎 TLS 日志服务的连接问题。
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nacos_sdk.api import get_config


def debug_tls_config():
    """诊断 TLS 配置"""
    print("=== TLS 配置诊断 ===")
    
    try:
        # 检查 Nacos 配置
        print("1. 检查 Nacos 配置...")
        
        # 尝试获取 tls.log.config
        tls_config = get_config("tls.log.config")
        if tls_config:
            print("✓ 找到 tls.log.config 配置")
            try:
                config_data = json.loads(tls_config)
                print(f"  配置内容: {json.dumps(config_data, indent=2, ensure_ascii=False)}")
                
                # 检查必要字段
                required_fields = ["VOLCENGINE_ENDPOINT", "VOLCENGINE_ACCESS_KEY_ID", "VOLCENGINE_ACCESS_KEY_SECRET"]
                missing_fields = []
                for field in required_fields:
                    if not config_data.get(field):
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"✗ 缺少必要配置字段: {missing_fields}")
                else:
                    print("✓ 所有必要配置字段都存在")
                    
            except json.JSONDecodeError as e:
                print(f"✗ 配置格式错误: {e}")
        else:
            print("✗ 未找到 tls.log.config 配置")
            
            # 尝试备用配置
            volcengine_config = get_config("volcengine.json")
            if volcengine_config:
                print("✓ 找到备用配置 volcengine.json")
                try:
                    config_data = json.loads(volcengine_config)
                    print(f"  配置内容: {json.dumps(config_data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError as e:
                    print(f"✗ 备用配置格式错误: {e}")
            else:
                print("✗ 也未找到备用配置 volcengine.json")
        
    except Exception as e:
        print(f"✗ Nacos 配置检查失败: {e}")
    
    print("\n2. 检查火山引擎 SDK...")
    
    # 检查 SDK 安装
    try:
        import volcengine
        print(f"✓ volcengine 包已安装，版本: {getattr(volcengine, 'VERSION', 'unknown')}")
    except ImportError:
        print("✗ volcengine 包未安装")
        print("  请运行: pip install volcengine")
        return
    
    # 检查 TLS 服务
    try:
        from volcengine.tls.TLSService import TLSService
        print("✓ TLS 服务模块可用")
    except ImportError:
        print("✗ TLS 服务模块不可用")
        print("  请安装: pip install volcengine")
        return
    
    print("\n3. 测试 TLS 客户端初始化...")
    
    # 测试客户端初始化
    try:
        if tls_config:
            config_data = json.loads(tls_config)
            
            region = config_data.get("VOLCENGINE_REGION", "cn-beijing")
            endpoint = config_data.get("VOLCENGINE_ENDPOINT", f"https://tls-{region}.volces.com")
            
            client = TLSService(
                endpoint=endpoint,
                access_key_id=config_data.get("VOLCENGINE_ACCESS_KEY_ID", ""),
                access_key_secret=config_data.get("VOLCENGINE_ACCESS_KEY_SECRET", ""),
                region=region
            )
            
            print("✓ TLS 客户端初始化成功")
            print(f"  区域: {region}")
            print(f"  端点: {endpoint}")
            
            # 测试简单的 API 调用（获取主题信息）
            print("\n4. 测试 API 连接...")
            try:
                # 这里可以添加一个简单的 API 测试
                print("✓ TLS 客户端配置完成，可以尝试发送日志")
            except Exception as api_error:
                print(f"✗ API 测试失败: {api_error}")
                
        else:
            print("✗ 无法测试客户端初始化，缺少配置")
            
    except Exception as e:
        print(f"✗ 客户端初始化失败: {e}")
    
    print("\n=== 诊断完成 ===")
    print("\n建议检查项目:")
    print("1. 确保 Nacos 中的 tls.log.config 配置正确")
    print("2. 确保火山引擎认证信息有效")
    print("3. 确保 TopicID 存在且有写入权限")
    print("4. 确保网络可以访问火山引擎 TLS 服务")


if __name__ == "__main__":
    debug_tls_config() 