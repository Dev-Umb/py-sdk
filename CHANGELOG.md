# Changelog

本文档记录了 py-sdk 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2025-01-XX

### 新增
- 🎉 首次发布 py-sdk
- 🔧 零配置启动支持
- 📋 统一日志管理，自动包含 TraceID
- 🌐 标准化 HTTP 客户端
- 🔗 异步安全的上下文管理
- 🎯 基于 Nacos 的服务注册发现
- 📊 完整的链路追踪和日志聚合
- 🔥 火山引擎 TLS 日志支持
- 🚀 Web 框架中间件支持（FastAPI、Flask、Django）
- 📦 标准化的 Python 包配置
- 🛠 自动化环境配置脚本
- 📚 完整的文档和示例代码

### 功能特性
- **上下文管理**: 自动生成 TraceID，支持异步安全传递
- **日志管理**: 结构化日志，支持多种输出方式
- **HTTP 客户端**: 统一响应格式，业务状态码支持
- **服务发现**: Nacos 配置热更新，服务健康检查
- **中间件**: 开箱即用的 Web 框架集成
- **可观测性**: 完整的链路追踪支持

### 依赖管理
- 基础依赖：requests, urllib3, contextvars, python-dotenv
- 可选依赖：
  - `[tls]`: 火山引擎 TLS 支持
  - `[web]`: Web 框架支持
  - `[dev]`: 开发工具支持
  - `[all]`: 所有功能支持

### 安装方式
```bash
# 基础安装
pip install py_sdk

# 完整安装
pip install py_sdk[all]

# 或者 git clone 方式
git clone <repo-url>
cd py_sdk
pip install -e .
```

### 文档
- [快速开始](docs/README.md)
- [API 文档](docs/)
- [示例代码](examples/)
- [常见问题](docs/faq.md) 