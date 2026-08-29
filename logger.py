import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

def get_logger(name="ai_agent"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加 Handler
    if logger.handlers:
        return logger

    # 日志输出格式：[时间] [级别] [文件名:行号] - 消息
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 1. 控制台 Handler (终端实时打印)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 轮转文件 Handler (单文件最大 5MB，最多保留 3 个备份)
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=5 * 1024 * 1024, 
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 导出全局单例
logger = get_logger()