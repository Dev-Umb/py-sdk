"""
日志系统性能测试示例

测试在高并发、大请求量情况下的性能表现，
对比同步和异步模式的性能差异。
"""

# 添加当前目录到Python路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
import concurrent.futures
from context.manager import create_context
from logger import init_logger, get_logger, is_logger_initialized


def performance_test_sync():
    """同步模式性能测试"""
    print("=== 同步模式性能测试 ===")
    
    # 初始化同步模式logger
    init_logger(
        level="INFO",
        console=False,  # 关闭控制台输出以减少干扰
        file="sync_test.log",
        tls=False,  # 关闭TLS以专注测试本地性能
        high_performance=False  # 使用同步模式
    )
    
    logger = get_logger("sync-test")
    
    # 测试参数
    num_threads = 50
    logs_per_thread = 100
    total_logs = num_threads * logs_per_thread
    
    print(f"测试参数: {num_threads} 线程，每线程 {logs_per_thread} 条日志，总计 {total_logs} 条")
    
    def log_worker(thread_id):
        """工作线程函数"""
        for i in range(logs_per_thread):
            ctx = create_context()
            logger.info(ctx, f"同步测试日志 线程{thread_id} 第{i}条", extra={
                "thread_id": thread_id,
                "log_index": i,
                "test_mode": "sync"
            })
    
    # 执行测试
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(log_worker, i) for i in range(num_threads)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"同步模式结果:")
    print(f"  总耗时: {duration:.2f} 秒")
    print(f"  平均QPS: {total_logs / duration:.2f}")
    print(f"  平均延迟: {duration / total_logs * 1000:.2f} ms/条")
    
    return duration, total_logs / duration


def performance_test_async():
    """异步模式性能测试"""
    print("\n=== 异步模式性能测试 ===")
    
    # 重新初始化为异步模式
    # 注意：这里会被忽略，因为logger已经初始化过了
    # 在实际使用中，应该在程序开始时就决定使用哪种模式
    
    # 为了演示，我们直接创建一个新的logger实例
    from logger.manager import LoggerManager
    
    async_config = {
        "level": "INFO",
        "handlers": {
            "console": {"enabled": False},
            "file": {
                "enabled": True,
                "filename": "async_test.log",
                "level": "INFO"
            },
            "tls": {"enabled": False}
        }
    }
    
    # 创建新的logger管理器实例进行测试
    async_manager = LoggerManager()
    async_manager.init_from_config(async_config)
    async_logger = async_manager.get_logger("async-test")
    
    # 测试参数
    num_threads = 50
    logs_per_thread = 100
    total_logs = num_threads * logs_per_thread
    
    print(f"测试参数: {num_threads} 线程，每线程 {logs_per_thread} 条日志，总计 {total_logs} 条")
    
    def log_worker(thread_id):
        """工作线程函数"""
        for i in range(logs_per_thread):
            ctx = create_context()
            async_logger.info(ctx, f"异步测试日志 线程{thread_id} 第{i}条", extra={
                "thread_id": thread_id,
                "log_index": i,
                "test_mode": "async"
            })
    
    # 执行测试
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(log_worker, i) for i in range(num_threads)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"异步模式结果:")
    print(f"  总耗时: {duration:.2f} 秒")
    print(f"  平均QPS: {total_logs / duration:.2f}")
    print(f"  平均延迟: {duration / total_logs * 1000:.2f} ms/条")
    
    # 关闭异步管理器
    async_manager.close()
    
    return duration, total_logs / duration


def tls_performance_test():
    """TLS异步模式性能测试"""
    print("\n=== TLS异步模式性能测试 ===")
    
    # 初始化TLS异步模式
    init_logger(
        level="INFO",
        console=False,
        tls={
            "batch_size": 50,       # 批量大小
            "batch_timeout": 2.0,   # 批量超时
            "queue_size": 5000,     # 队列大小
            "worker_threads": 2,    # 工作线程数
            "retry_times": 3        # 重试次数
        },
        topic_id="test-topic-id",
        service_name="performance-test",
        high_performance=True
    )
    
    logger = get_logger("tls-async-test")
    
    # 测试参数（较少的日志量，因为要发送到网络）
    num_threads = 20
    logs_per_thread = 25
    total_logs = num_threads * logs_per_thread
    
    print(f"测试参数: {num_threads} 线程，每线程 {logs_per_thread} 条日志，总计 {total_logs} 条")
    print("注意: TLS日志会异步批量发送，不会阻塞主线程")
    
    def log_worker(thread_id):
        """工作线程函数"""
        for i in range(logs_per_thread):
            ctx = create_context()
            logger.info(ctx, f"TLS异步测试日志 线程{thread_id} 第{i}条", extra={
                "thread_id": thread_id,
                "log_index": i,
                "test_mode": "tls_async",
                "performance_test": True
            })
    
    # 执行测试
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(log_worker, i) for i in range(num_threads)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"TLS异步模式结果:")
    print(f"  总耗时: {duration:.2f} 秒")
    print(f"  平均QPS: {total_logs / duration:.2f}")
    print(f"  平均延迟: {duration / total_logs * 1000:.2f} ms/条")
    print("  注意: 这是客户端性能，实际网络发送在后台异步进行")
    
    # 等待一段时间让异步发送完成
    print("等待异步发送完成...")
    time.sleep(5)
    
    return duration, total_logs / duration


def memory_usage_test():
    """内存使用测试"""
    print("\n=== 内存使用测试 ===")
    
    try:
        import psutil
        process = psutil.Process()
        
        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"初始内存使用: {initial_memory:.2f} MB")
        
        # 大量日志测试
        logger = get_logger("memory-test")
        num_logs = 10000
        
        print(f"开始记录 {num_logs} 条日志...")
        start_time = time.time()
        
        for i in range(num_logs):
            ctx = create_context()
            logger.info(ctx, f"内存测试日志 第{i}条", extra={
                "log_index": i,
                "test_data": "x" * 100,  # 添加一些数据
                "timestamp": time.time()
            })
            
            # 每1000条检查一次内存
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"  记录 {i} 条后内存使用: {current_memory:.2f} MB")
        
        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        print(f"最终内存使用: {final_memory:.2f} MB")
        print(f"内存增长: {final_memory - initial_memory:.2f} MB")
        print(f"总耗时: {end_time - start_time:.2f} 秒")
        
    except ImportError:
        print("需要安装 psutil 包来进行内存测试: pip install psutil")


def main():
    """主函数"""
    print("日志系统性能测试")
    print("=" * 60)
    
    # 运行各种性能测试
    sync_duration, sync_qps = performance_test_sync()
    async_duration, async_qps = performance_test_async()
    tls_duration, tls_qps = tls_performance_test()
    
    # 内存使用测试
    memory_usage_test()
    
    # 性能对比总结
    print("\n" + "=" * 60)
    print("性能对比总结")
    print("=" * 60)
    print(f"同步模式:     QPS = {sync_qps:.2f}")
    print(f"异步模式:     QPS = {async_qps:.2f}")
    print(f"TLS异步模式:  QPS = {tls_qps:.2f}")
    print(f"异步提升:     {async_qps / sync_qps:.2f}x")
    
    print("\n性能建议:")
    print("1. 对于高并发应用，推荐使用异步模式 (high_performance=True)")
    print("2. TLS日志使用批量发送，不会阻塞主线程")
    print("3. 可以通过调整batch_size和worker_threads来优化性能")
    print("4. 在超高QPS场景下，考虑调整queue_size避免日志丢失")


if __name__ == "__main__":
    main() 