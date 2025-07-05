#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 基础依赖
base_requirements = [
    "requests>=2.32.4",
    "urllib3>=1.26.20,<3.0.0",
    "contextvars>=2.4",
    "python-dotenv>=0.19.0",
]

# 可选依赖组
extras_require = {
    # 火山引擎 TLS 支持
    "tls": [
        "volcengine>=1.0.184",
        "lz4>=4.0.0",
    ],
    # Web 框架支持
    "web": [
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "flask>=2.0.0",
        "django>=3.2.0",
        "tornado>=6.0.0",
    ],
    # 开发依赖
    "dev": [
        "pytest>=6.0.0",
        "pytest-asyncio>=0.18.0",
        "pytest-cov>=2.12.0",
        "black>=21.0.0",
        "flake8>=3.9.0",
        "mypy>=0.910",
    ],
}

# 完整安装（包含所有可选依赖）
extras_require["all"] = sum(extras_require.values(), [])

setup(
    name="py-sdk",
    version="1.0.0",
    author="Your Team",
    author_email="your-email@example.com",
    description="Python 微服务通用 SDK - 提供统一的日志管理、HTTP 客户端、上下文管理和服务注册发现等功能",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/py-sdk",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.7",
    install_requires=base_requirements,
    extras_require=extras_require,
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
    },
    entry_points={
        "console_scripts": [
            "py-sdk-setup=py_sdk.scripts.setup:main",
        ],
    },
    keywords="microservice sdk logging http nacos context tracing",
    project_urls={
        "Bug Reports": "https://github.com/your-org/py-sdk/issues",
        "Source": "https://github.com/your-org/py-sdk",
        "Documentation": "https://github.com/your-org/py-sdk/blob/main/docs/README.md",
    },
) 