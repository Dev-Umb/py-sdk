#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nacos配置获取API使用示例

这个示例展示了如何使用nacos.api模块来获取配置
"""

from nacos_sdk import get_config

def main():
    """主函数，演示配置获取"""
    
    print("=== Nacos配置获取示例 ===")
    
    # 示例1: 获取默认分组的配置
    print("\n1. 获取默认分组配置:")
    config1 = get_config("ai.service.prompt")
    if config1:
        print(f"配置内容:\n{config1}")
    else:
        print("配置不存在或获取失败")
    
    # 示例2: 获取指定分组的配置
    print("\n2. 获取指定分组配置:")
    config2 = get_config("ai.service.prompt", "DEV_GROUP")
    if config2:
        print(f"配置内容:\n{config2}")
    else:
        print("配置不存在或获取失败")
    
    # 示例3: 获取JSON格式配置
    print("\n3. 获取JSON配置:")
    config3 = get_config("service.json", "DEFAULT_GROUP")
    if config3:
        print(f"配置内容:\n{config3}")
        # 如果是JSON格式，可以进一步解析
        try:
            import json
            parsed_config = json.loads(config3)
            print(f"解析后的配置: {parsed_config}")
        except json.JSONDecodeError:
            print("配置不是有效的JSON格式")
    else:
        print("配置不存在或获取失败")

if __name__ == "__main__":
    main()
