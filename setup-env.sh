#!/bin/bash

# ================================
# Python SDK 环境变量配置设置脚本
# ================================
# 这个脚本帮助用户快速设置环境变量配置

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Python SDK 环境变量配置设置${NC}"
echo -e "${GREEN}================================${NC}"

# 检查 env.example 文件是否存在
if [ ! -f "env.example" ]; then
    echo -e "${RED}❌ 找不到 env.example 文件${NC}"
    echo -e "${YELLOW}请确保在项目根目录下运行此脚本${NC}"
    exit 1
fi

# 检查是否已存在 .env 文件
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  发现已存在的 .env 文件${NC}"
    read -p "是否要覆盖现有的 .env 文件？(y/N): " choice
    case "$choice" in
        y|Y )
            echo -e "${GREEN}✅ 将覆盖现有的 .env 文件${NC}"
            ;;
        * )
            echo -e "${GREEN}✅ 保留现有的 .env 文件${NC}"
            echo -e "${CYAN}💡 您可以手动编辑 .env 文件或参考 env.example${NC}"
            exit 0
            ;;
    esac
fi

# 复制 env.example 为 .env
if cp env.example .env; then
    echo -e "${GREEN}✅ 成功创建 .env 文件${NC}"
else
    echo -e "${RED}❌ 创建 .env 文件失败${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}🔧 接下来请编辑 .env 文件，设置实际的配置值：${NC}"
echo ""

# 显示需要修改的重要配置项
echo -e "${YELLOW}📝 重要配置项（请根据实际情况修改）：${NC}"
echo -e "${WHITE}  • NACOS_SERVER_ADDRESSES - Nacos 服务器地址${NC}"
echo -e "${WHITE}  • NACOS_NAMESPACE - 命名空间（如：dev, test, prod）${NC}"
echo -e "${WHITE}  • NACOS_USERNAME - Nacos 用户名（如果启用认证）${NC}"
echo -e "${WHITE}  • NACOS_PASSWORD - Nacos 密码（如果启用认证）${NC}"
echo -e "${WHITE}  • TLS_TOPIC_ID - 火山引擎 TLS Topic ID${NC}"
echo -e "${WHITE}  • TLS_ACCESS_KEY_ID - 火山引擎访问密钥 ID${NC}"
echo -e "${WHITE}  • TLS_ACCESS_KEY_SECRET - 火山引擎访问密钥${NC}"
echo -e "${WHITE}  • APP_NAME - 应用名称${NC}"
echo -e "${WHITE}  • APP_VERSION - 应用版本${NC}"
echo -e "${WHITE}  • APP_ENV - 运行环境${NC}"

echo ""
echo -e "${CYAN}💡 使用提示：${NC}"
echo -e "${WHITE}  1. 使用文本编辑器打开 .env 文件${NC}"
echo -e "${WHITE}  2. 修改配置值（去掉注释符号 # 并设置实际值）${NC}"
echo -e "${WHITE}  3. 保存文件后重启应用${NC}"
echo -e "${WHITE}  4. 运行测试脚本验证配置：python examples/env_config_example.py${NC}"

echo ""
echo -e "${CYAN}🎯 常用命令：${NC}"
echo -e "${WHITE}  • 编辑配置文件: vim .env 或 nano .env${NC}"
echo -e "${WHITE}  • 加载环境变量: source .env${NC}"
echo -e "${WHITE}  • 测试配置: python examples/env_config_example.py${NC}"
echo -e "${WHITE}  • 查看完整示例: python examples/nacos_env_example.py${NC}"

echo ""
echo -e "${CYAN}📚 更多信息：${NC}"
echo -e "${WHITE}  • 文档: docs/config.md${NC}"
echo -e "${WHITE}  • 示例: examples/${NC}"
echo -e "${WHITE}  • 问题排查: docs/faq.md${NC}"

echo ""
echo -e "${GREEN}🎉 环境变量配置设置完成！${NC}"

# 询问是否立即打开编辑器
read -p "是否立即打开编辑器编辑 .env 文件？(y/N): " editNow
case "$editNow" in
    y|Y )
        # 尝试使用不同的编辑器
        if command -v code &> /dev/null; then
            code .env
            echo -e "${GREEN}✅ 已用 VS Code 打开编辑器${NC}"
        elif command -v vim &> /dev/null; then
            vim .env
            echo -e "${GREEN}✅ 已用 Vim 打开编辑器${NC}"
        elif command -v nano &> /dev/null; then
            nano .env
            echo -e "${GREEN}✅ 已用 Nano 打开编辑器${NC}"
        else
            echo -e "${YELLOW}⚠️  未找到可用的编辑器，请手动编辑 .env 文件${NC}"
        fi
        ;;
    * )
        echo -e "${CYAN}💡 您可以稍后使用 vim .env 或 nano .env 编辑配置文件${NC}"
        ;;
esac

echo ""
echo -e "${GREEN}感谢使用 Python SDK！${NC}" 