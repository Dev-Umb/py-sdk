# ================================
# Python SDK 环境变量配置设置脚本
# ================================
# 这个脚本帮助用户快速设置环境变量配置

Write-Host "🚀 Python SDK 环境变量配置设置" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 检查 env.example 文件是否存在
if (-not (Test-Path "env.example")) {
    Write-Host "❌ 找不到 env.example 文件" -ForegroundColor Red
    Write-Host "请确保在项目根目录下运行此脚本" -ForegroundColor Yellow
    exit 1
}

# 检查是否已存在 .env 文件
if (Test-Path ".env") {
    Write-Host "⚠️  发现已存在的 .env 文件" -ForegroundColor Yellow
    $choice = Read-Host "是否要覆盖现有的 .env 文件？(y/N)"
    if ($choice -ne "y" -and $choice -ne "Y") {
        Write-Host "✅ 保留现有的 .env 文件" -ForegroundColor Green
        Write-Host "💡 您可以手动编辑 .env 文件或参考 env.example" -ForegroundColor Cyan
        exit 0
    }
}

# 复制 env.example 为 .env
try {
    Copy-Item "env.example" ".env"
    Write-Host "✅ 成功创建 .env 文件" -ForegroundColor Green
} catch {
    Write-Host "❌ 创建 .env 文件失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 接下来请编辑 .env 文件，设置实际的配置值：" -ForegroundColor Cyan
Write-Host ""

# 显示需要修改的重要配置项
Write-Host "📝 重要配置项（请根据实际情况修改）：" -ForegroundColor Yellow
Write-Host "  • NACOS_SERVER_ADDRESSES - Nacos 服务器地址" -ForegroundColor White
Write-Host "  • NACOS_NAMESPACE - 命名空间（如：dev, test, prod）" -ForegroundColor White
Write-Host "  • NACOS_USERNAME - Nacos 用户名（如果启用认证）" -ForegroundColor White
Write-Host "  • NACOS_PASSWORD - Nacos 密码（如果启用认证）" -ForegroundColor White
Write-Host "  • TLS_TOPIC_ID - 火山引擎 TLS Topic ID" -ForegroundColor White
Write-Host "  • TLS_ACCESS_KEY_ID - 火山引擎访问密钥 ID" -ForegroundColor White
Write-Host "  • TLS_ACCESS_KEY_SECRET - 火山引擎访问密钥" -ForegroundColor White
Write-Host "  • APP_NAME - 应用名称" -ForegroundColor White
Write-Host "  • APP_VERSION - 应用版本" -ForegroundColor White
Write-Host "  • APP_ENV - 运行环境" -ForegroundColor White

Write-Host ""
Write-Host "💡 使用提示：" -ForegroundColor Cyan
Write-Host "  1. 使用文本编辑器打开 .env 文件" -ForegroundColor White
Write-Host "  2. 修改配置值（去掉注释符号 # 并设置实际值）" -ForegroundColor White
Write-Host "  3. 保存文件后重启应用" -ForegroundColor White
Write-Host "  4. 运行测试脚本验证配置：python examples/env_config_example.py" -ForegroundColor White

Write-Host ""
Write-Host "🎯 常用命令：" -ForegroundColor Cyan
Write-Host "  • 编辑配置文件: notepad .env" -ForegroundColor White
Write-Host "  • 测试配置: python examples/env_config_example.py" -ForegroundColor White
Write-Host "  • 查看完整示例: python examples/nacos_env_example.py" -ForegroundColor White

Write-Host ""
Write-Host "📚 更多信息：" -ForegroundColor Cyan
Write-Host "  • 文档: docs/config.md" -ForegroundColor White
Write-Host "  • 示例: examples/" -ForegroundColor White
Write-Host "  • 问题排查: docs/faq.md" -ForegroundColor White

Write-Host ""
Write-Host "🎉 环境变量配置设置完成！" -ForegroundColor Green

# 询问是否立即打开编辑器
$editNow = Read-Host "是否立即打开编辑器编辑 .env 文件？(y/N)"
if ($editNow -eq "y" -or $editNow -eq "Y") {
    try {
        Start-Process notepad ".env"
        Write-Host "✅ 已打开编辑器" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  无法打开编辑器，请手动编辑 .env 文件" -ForegroundColor Yellow
    }
} 