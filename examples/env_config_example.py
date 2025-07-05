#!/usr/bin/env python3
"""
环境变量配置使用示例

这个示例展示了如何使用 env.example 文件来配置 SDK。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_env_file(env_file_path):
    """
    简单的 .env 文件加载器
    
    Args:
        env_file_path: .env 文件路径
    """
    if not os.path.exists(env_file_path):
        print(f"❌ 环境变量文件不存在: {env_file_path}")
        return False
    
    print(f"📋 加载环境变量文件: {env_file_path}")
    
    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析环境变量
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # 设置环境变量
                os.environ[key] = value
                print(f"  ✅ {key}={value}")
            else:
                print(f"  ⚠️  第 {line_num} 行格式错误: {line}")
    
    return True

def show_current_config():
    """显示当前的环境变量配置"""
    print("\n🔧 当前环境变量配置:")
    
    # SDK 相关的环境变量
    sdk_env_vars = [
        'NACOS_SERVER_ADDRESSES',
        'NACOS_NAMESPACE', 
        'NACOS_USERNAME',
        'NACOS_PASSWORD',
        'LOG_LEVEL',
        'LOG_FORMAT',
        'TLS_ENDPOINT',
        'TLS_TOPIC_ID',
        'TLS_ACCESS_KEY_ID',
        'TLS_ACCESS_KEY_SECRET',
        'HTTP_TIMEOUT',
        'HTTP_RETRIES',
        'APP_NAME',
        'APP_VERSION',
        'APP_ENV',
        'APP_PORT',
        'DEBUG',
        'PY_SDK_AUTO_INIT'
    ]
    
    for var in sdk_env_vars:
        value = os.environ.get(var)
        if value:
            # 隐藏敏感信息
            if any(sensitive in var.lower() for sensitive in ['password', 'secret', 'key']):
                display_value = '*' * len(value) if len(value) > 0 else 'NOT_SET'
            else:
                display_value = value
            print(f"  {var}: {display_value}")
        else:
            print(f"  {var}: NOT_SET")

def test_nacos_with_env():
    """测试使用环境变量配置 Nacos"""
    print("\n🎯 测试 Nacos 环境变量配置:")
    
    try:
        from nacos.client import NacosClient
        
        # 使用环境变量创建客户端
        client = NacosClient()
        
        print(f"  ✅ Nacos 客户端创建成功")
        print(f"     服务器地址: {client.server_addresses}")
        print(f"     命名空间: '{client.namespace}'")
        print(f"     用户名: {client.username}")
        print(f"     密码: {'*' * len(client.password) if client.password else 'NOT_SET'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 创建 Nacos 客户端失败: {e}")
        return False

def test_logger_with_env():
    """测试使用环境变量配置日志"""
    print("\n📝 测试日志环境变量配置:")
    
    try:
        from logger import get_logger
        from context import create_context
        
        logger = get_logger("env-test")
        
        # 检查日志级别
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        print(f"  ✅ 日志记录器创建成功")
        print(f"     日志级别: {log_level}")
        
        # 测试日志输出（需要上下文）
        ctx = create_context()
        logger.info(ctx, "这是一条测试日志消息")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 创建日志记录器失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 环境变量配置示例")
    print("=" * 50)
    
    # 项目根目录
    project_root = Path(__file__).parent.parent
    env_example_path = project_root / "env.example"
    env_file_path = project_root / ".env"
    
    print(f"📁 项目根目录: {project_root}")
    print(f"📋 示例文件: {env_example_path}")
    print(f"📋 配置文件: {env_file_path}")
    
    # 检查文件是否存在
    if not env_example_path.exists():
        print(f"❌ 找不到示例文件: {env_example_path}")
        return
    
    # 选择加载哪个文件
    if env_file_path.exists():
        print(f"\n📋 发现 .env 文件，加载用户配置...")
        load_env_file(str(env_file_path))
    else:
        print(f"\n📋 未找到 .env 文件，使用示例配置...")
        print(f"💡 提示: 可以运行 'cp {env_example_path} {env_file_path}' 创建配置文件")
        load_env_file(str(env_example_path))
    
    # 显示当前配置
    show_current_config()
    
    # 测试各个组件
    nacos_ok = test_nacos_with_env()
    logger_ok = test_logger_with_env()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"  Nacos 配置: {'✅ 成功' if nacos_ok else '❌ 失败'}")
    print(f"  日志配置: {'✅ 成功' if logger_ok else '❌ 失败'}")
    
    if nacos_ok and logger_ok:
        print("\n🎉 所有配置测试通过！SDK 已准备就绪。")
    else:
        print("\n⚠️  部分配置测试失败，请检查环境变量设置。")
    
    print("\n💡 使用提示:")
    print("  1. 复制 env.example 为 .env: cp env.example .env")
    print("  2. 编辑 .env 文件，设置实际的配置值")
    print("  3. 重新运行此脚本验证配置")

if __name__ == "__main__":
    main() 