from prometheus_client import start_http_server, Counter

# 定义 2 个核心监控指标
JOBS_PROCESSED = Counter('agent_jobs_processed_total', '已处理的任务总数')
PUSH_ERRORS = Counter('agent_push_errors_total', '推送失败总次数')

def init_metrics(port=8000):
    """静默启动 Prometheus 监控端口，即使端口冲突也不影响主程序运行"""
    try:
        start_http_server(port)
    except Exception:
        pass