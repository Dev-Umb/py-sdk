#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nacos SDK 模块示例

演示如何使用 nacos_sdk 模块进行服务注册发现和配置管理，
包括服务注册、配置获取、健康检查等功能。
"""

import time
import signal
import sys
import json
import threading
from nacos_sdk import registerNacos, unregisterNacos, get_config
from context import create_context
from logger import init_logger_manager, get_logger


def main():
    """主函数"""
    print("🎯 Nacos SDK 模块示例")
    print("=" * 50)
    
    # 初始化日志
    init_logger_manager(service_name="nacos-example")
    
    # 1. 服务注册
    print("\n📋 1. 服务注册")
    service_registration()
    
    # 2. 配置管理
    print("\n📋 2. 配置管理")
    configuration_management()
    
    # 3. 服务运行模拟
    print("\n📋 3. 服务运行模拟")
    service_runtime_simulation()
    
    print("\n" + "=" * 50)
    print("✅ Nacos SDK 示例完成！")


def service_registration():
    """服务注册示例"""
    print("服务注册演示...")
    
    logger = get_logger("service-registry")
    ctx = create_context()
    
    # 基础服务注册
    print("\n  基础服务注册:")
    success = registerNacos(
        service_name="example-service",
        port=8080,
        metadata={
            "version": "1.0.0",
            "env": "dev",
            "team": "backend"
        }
    )
    
    if success:
        logger.info(ctx, "服务注册成功", extra={
            "service_name": "example-service",
            "port": 8080
        })
        print("  ✓ 基础服务注册成功")
    else:
        logger.error(ctx, "服务注册失败")
        print("  ✗ 基础服务注册失败")
    
    # 多服务注册示例
    print("\n  多服务注册:")
    services = [
        {
            "name": "user-service",
            "port": 8081,
            "metadata": {"module": "user", "version": "1.0.0"}
        },
        {
            "name": "order-service", 
            "port": 8082,
            "metadata": {"module": "order", "version": "1.0.0"}
        },
        {
            "name": "payment-service",
            "port": 8083,
            "metadata": {"module": "payment", "version": "1.0.0"}
        }
    ]
    
    for service in services:
        success = registerNacos(
            service_name=service["name"],
            port=service["port"],
            metadata=service["metadata"]
        )
        
        if success:
            logger.info(ctx, "服务注册成功", extra={
                "service_name": service["name"],
                "port": service["port"]
            })
            print(f"  ✓ {service['name']} 注册成功")
        else:
            logger.error(ctx, "服务注册失败", extra={
                "service_name": service["name"]
            })
            print(f"  ✗ {service['name']} 注册失败")
    
    time.sleep(2)  # 等待注册完成


def configuration_management():
    """配置管理示例"""
    print("配置管理演示...")
    
    logger = get_logger("config-manager")
    ctx = create_context()
    
    # 获取应用配置
    print("\n  获取应用配置:")
    app_config = get_config("app.json")
    if app_config:
        try:
            config_data = json.loads(app_config)
            logger.info(ctx, "应用配置获取成功", extra={
                "config_keys": list(config_data.keys())
            })
            print(f"  ✓ 应用配置: {config_data}")
        except json.JSONDecodeError:
            logger.error(ctx, "应用配置格式错误")
            print(f"  ✗ 配置格式错误: {app_config}")
    else:
        logger.warning(ctx, "应用配置不存在")
        print("  ⚠ 应用配置不存在，使用默认配置")
        # 使用默认配置
        default_config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "name": "example_db"
            },
            "redis": {
                "host": "localhost",
                "port": 6379
            },
            "log_level": "INFO"
        }
        print(f"  ✓ 默认配置: {default_config}")
    
    # 获取数据库配置
    print("\n  获取数据库配置:")
    db_config = get_config("database.yml")
    if db_config:
        logger.info(ctx, "数据库配置获取成功")
        print(f"  ✓ 数据库配置: {db_config}")
    else:
        logger.warning(ctx, "数据库配置不存在")
        print("  ⚠ 数据库配置不存在")
    
    # 获取不同分组的配置
    print("\n  获取不同分组配置:")
    groups = ["DEFAULT_GROUP", "DEV_GROUP", "PROD_GROUP"]
    
    for group in groups:
        config = get_config("service.properties", group)
        if config:
            logger.info(ctx, "配置获取成功", extra={
                "group": group,
                "config_length": len(config)
            })
            print(f"  ✓ {group}: {config[:50]}...")
        else:
            logger.info(ctx, "配置不存在", extra={"group": group})
            print(f"  - {group}: 配置不存在")


def service_runtime_simulation():
    """服务运行模拟"""
    print("服务运行模拟...")
    
    logger = get_logger("service-runtime")
    ctx = create_context()
    
    # 注册信号处理器
    def signal_handler(sig, frame):
        logger.info(ctx, "接收到退出信号，开始清理...")
        print("\n  接收到退出信号，正在注销服务...")
        
        # 注销所有服务
        services = [
            ("example-service", 8080),
            ("user-service", 8081),
            ("order-service", 8082),
            ("payment-service", 8083)
        ]
        
        for service_name, port in services:
            success = unregisterNacos(service_name, port)
            if success:
                logger.info(ctx, "服务注销成功", extra={
                    "service_name": service_name,
                    "port": port
                })
                print(f"  ✓ {service_name} 注销成功")
            else:
                logger.error(ctx, "服务注销失败", extra={
                    "service_name": service_name
                })
                print(f"  ✗ {service_name} 注销失败")
        
        print("  清理完成，退出程序")
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动配置监听
    config_watcher = ConfigWatcher()
    config_watcher.start()
    
    # 模拟服务运行
    print("\n  服务运行中...")
    print("  按 Ctrl+C 退出")
    
    try:
        # 模拟业务处理
        for i in range(10):
            logger.info(ctx, "处理业务请求", extra={
                "request_id": f"REQ-{i+1:03d}",
                "processing_time": 100 + i * 10
            })
            print(f"  处理请求 {i+1}/10")
            time.sleep(1)
        
        print("\n  模拟运行完成")
        
    except KeyboardInterrupt:
        # 手动触发信号处理器
        signal_handler(signal.SIGINT, None)


class ConfigWatcher:
    """配置监听器"""
    
    def __init__(self):
        self.logger = get_logger("config-watcher")
        self.ctx = create_context()
        self.running = False
        self.thread = None
        self.last_config_hash = {}
    
    def start(self):
        """启动配置监听"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_config, daemon=True)
        self.thread.start()
        
        self.logger.info(ctx,self.ctx, "配置监听器启动")
        print("  ✓ 配置监听器启动")
    
    def stop(self):
        """停止配置监听"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        self.logger.info(ctx,self.ctx, "配置监听器停止")
        print("  ✓ 配置监听器停止")
    
    def _watch_config(self):
        """监听配置变化"""
        configs_to_watch = [
            ("app.json", "DEFAULT_GROUP"),
            ("database.yml", "DEFAULT_GROUP"),
            ("service.properties", "DEV_GROUP")
        ]
        
        while self.running:
            try:
                for data_id, group in configs_to_watch:
                    config = get_config(data_id, group)
                    if config:
                        config_hash = hash(config)
                        key = f"{data_id}#{group}"
                        
                        if key in self.last_config_hash:
                            if self.last_config_hash[key] != config_hash:
                                self.logger.info(ctx,self.ctx, "配置发生变化", extra={
                                    "data_id": data_id,
                                    "group": group,
                                    "config_length": len(config)
                                })
                                print(f"  📝 配置变化: {data_id} ({group})")
                                self._on_config_changed(data_id, group, config)
                        
                        self.last_config_hash[key] = config_hash
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(ctx,self.ctx, "配置监听异常", extra={
                    "error": str(e)
                })
                time.sleep(10)  # 异常时等待更长时间
    
    def _on_config_changed(self, data_id, group, config):
        """配置变化处理"""
        try:
            if data_id == "app.json":
                # 处理应用配置变化
                config_data = json.loads(config)
                self.logger.info(ctx,self.ctx, "应用配置已更新", extra={
                    "config_keys": list(config_data.keys())
                })
                
            elif data_id == "database.yml":
                # 处理数据库配置变化
                self.logger.info(ctx,self.ctx, "数据库配置已更新")
                
            elif data_id == "service.properties":
                # 处理服务配置变化
                self.logger.info(ctx,self.ctx, "服务配置已更新")
                
        except Exception as e:
            self.logger.error(ctx,self.ctx, "配置处理失败", extra={
                "data_id": data_id,
                "group": group,
                "error": str(e)
            })


if __name__ == "__main__":
    main() 