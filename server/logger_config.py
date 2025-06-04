# 日志配置
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging():
    """设置日志配置"""
    # 创建logs目录（如果不存在）
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, "server.log")
    
    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 如果已经有handlers，清除它们
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建文件handler（使用RotatingFileHandler进行日志轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式器
    file_formatter = logging.Formatter(
        '%(asctime)s[%(levelname)s]%(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式器
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # 添加handlers到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = __name__):
    """获取logger实例"""
    return logging.getLogger(name)


# 初始化日志
logger = setup_logging()
