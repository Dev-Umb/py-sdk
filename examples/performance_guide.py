"""
日志系统性能优化指南

针对不同的应用场景，提供性能优化建议和配置示例。
"""

# 添加当前目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import init_logger, get_logger
from context.manager import create_context


def low_traffic_app():
    """低流量应用配置示例"""
    print("=== 低流量应用 (< 1000 QPS) ===")
    
    # 简单配置，使用默认设置
    init_logger(
        level="INFO",
        console=True,
        file="app.log",
        tls=True,
        topic_id="your-topic-id",
        service_name="low-traffic-app"
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.info(ctx, "低流量应用启动")
    
    print("配置特点:")
    print("- 使用默认的异步模式")
    print("- 默认批量大小和超时时间")
    print("- 适合大多数Web应用")


def medium_traffic_app():
    """中等流量应用配置示例"""
    print("\n=== 中等流量应用 (1000-10000 QPS) ===")
    
    # 优化配置
    init_logger(
        level="INFO",
        console=False,  # 关闭控制台输出以提高性能
        file="app.log",
        tls={
            "batch_size": 200,      # 增加批量大小
            "batch_timeout": 3.0,   # 稍微增加超时时间
            "queue_size": 10000,    # 增加队列大小
            "worker_threads": 3,    # 增加工作线程
            "retry_times": 3
        },
        topic_id="your-topic-id",
        service_name="medium-traffic-app",
        high_performance=True
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.info(ctx, "中等流量应用启动")
    
    print("配置特点:")
    print("- 关闭控制台输出减少I/O开销")
    print("- 增加批量大小减少网络请求")
    print("- 增加队列大小应对流量突发")
    print("- 增加工作线程提高并发处理能力")


def high_traffic_app():
    """高流量应用配置示例"""
    print("\n=== 高流量应用 (> 10000 QPS) ===")
    
    # 高性能配置
    init_logger(
        level="WARNING",  # 只记录重要日志
        console=False,
        file=None,  # 关闭文件输出
        tls={
            "batch_size": 500,      # 大批量
            "batch_timeout": 1.0,   # 短超时快速发送
            "queue_size": 50000,    # 大队列
            "worker_threads": 6,    # 多工作线程
            "retry_times": 2        # 减少重试次数
        },
        topic_id="your-topic-id",
        service_name="high-traffic-app",
        high_performance=True
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.warning(ctx, "高流量应用启动")
    
    print("配置特点:")
    print("- 只记录WARNING及以上级别日志")
    print("- 关闭本地文件输出")
    print("- 大批量、大队列应对高并发")
    print("- 多工作线程并行处理")
    print("- 减少重试次数避免阻塞")


def microservice_app():
    """微服务应用配置示例"""
    print("\n=== 微服务应用 ===")
    
    # 微服务优化配置
    init_logger(
        level="INFO",
        console=False,
        file=None,  # 微服务通常不需要本地文件
        tls={
            "batch_size": 100,
            "batch_timeout": 2.0,
            "queue_size": 5000,
            "worker_threads": 2,
            "retry_times": 3
        },
        topic_id="microservice-topic",
        service_name="user-service",  # 明确的服务名
        high_performance=True
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.info(ctx, "微服务启动", extra={
        "service_name": "user-service",
        "version": "1.0.0",
        "instance_id": "user-service-001"
    })
    
    print("配置特点:")
    print("- 关闭本地文件输出，依赖集中式日志")
    print("- 明确的服务名称便于日志分析")
    print("- 适中的批量大小和队列大小")
    print("- 包含服务实例信息")


def batch_processing_app():
    """批处理应用配置示例"""
    print("\n=== 批处理应用 ===")
    
    # 批处理优化配置
    init_logger(
        level="INFO",
        console=True,   # 保留控制台输出便于监控
        file="batch.log",
        tls={
            "batch_size": 1000,     # 大批量适合批处理
            "batch_timeout": 10.0,  # 长超时时间
            "queue_size": 20000,    # 大队列
            "worker_threads": 4,
            "retry_times": 5        # 更多重试确保日志不丢失
        },
        topic_id="batch-topic",
        service_name="data-processor",
        high_performance=True
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.info(ctx, "批处理任务启动")
    
    print("配置特点:")
    print("- 保留控制台输出便于监控进度")
    print("- 大批量和长超时适合批处理场景")
    print("- 更多重试确保日志完整性")
    print("- 大队列应对批量数据处理")


def debug_development_app():
    """开发调试配置示例"""
    print("\n=== 开发调试模式 ===")
    
    # 开发调试配置
    init_logger(
        level="DEBUG",
        console=True,
        file="debug.log",
        tls=False,  # 开发环境可能不需要TLS
        high_performance=False  # 使用同步模式便于调试
    )
    
    logger = get_logger(__name__)
    ctx = create_context()
    
    logger.debug(ctx, "调试信息", extra={"debug_data": {"key": "value"}})
    logger.info(ctx, "应用启动")
    
    print("配置特点:")
    print("- DEBUG级别查看详细信息")
    print("- 同步模式便于调试")
    print("- 保留控制台和文件输出")
    print("- 关闭TLS减少外部依赖")


def performance_tips():
    """性能优化建议"""
    print("\n" + "=" * 60)
    print("性能优化建议")
    print("=" * 60)
    
    print("\n1. 日志级别优化:")
    print("   - 生产环境使用INFO或WARNING级别")
    print("   - 避免在高频路径中使用DEBUG级别")
    print("   - 关键错误使用ERROR级别")
    
    print("\n2. 输出方式选择:")
    print("   - 高性能场景关闭控制台输出")
    print("   - 微服务环境关闭文件输出")
    print("   - 使用异步TLS处理器")
    
    print("\n3. 批量配置调优:")
    print("   - 高QPS: 大批量(500+)，短超时(1-2s)")
    print("   - 低QPS: 小批量(50-100)，长超时(5-10s)")
    print("   - 批处理: 大批量(1000+)，长超时(10s+)")
    
    print("\n4. 队列和线程配置:")
    print("   - 队列大小 = 预期QPS × 批量超时时间")
    print("   - 工作线程数 = CPU核心数 / 2 到 CPU核心数")
    print("   - 监控队列使用率，避免日志丢失")
    
    print("\n5. 内存优化:")
    print("   - 避免在日志中包含大量数据")
    print("   - 使用结构化日志而非长字符串")
    print("   - 定期监控内存使用情况")
    
    print("\n6. 网络优化:")
    print("   - 调整重试次数和延迟")
    print("   - 监控网络延迟和错误率")
    print("   - 考虑使用压缩减少网络传输")


def main():
    """主函数"""
    print("日志系统性能优化指南")
    print("=" * 60)
    
    # 展示不同场景的配置
    low_traffic_app()
    medium_traffic_app()
    high_traffic_app()
    microservice_app()
    batch_processing_app()
    debug_development_app()
    
    # 性能优化建议
    performance_tips()
    
    print("\n" + "=" * 60)
    print("选择建议:")
    print("1. 根据应用的QPS选择合适的配置模板")
    print("2. 在生产环境中监控日志性能指标")
    print("3. 根据实际情况调整批量大小和队列大小")
    print("4. 定期检查日志丢失率和延迟")


if __name__ == "__main__":
    main() 