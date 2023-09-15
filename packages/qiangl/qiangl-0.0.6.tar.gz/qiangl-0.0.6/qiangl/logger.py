import sys
from loguru import logger
import qiangl.env as env


def setup_logger():
    # 获取当前程序所在的目录路径
    import os

    current_dir = env.getCurrentDir()

    # 创建日志文件夹
    log_dir = os.path.join(current_dir, "log")
    log_dir = os.path.join(log_dir, env.getToday())
    log_file = os.path.join(log_dir, f"{env.getToday()}.log")
    env.mkdir(log_file)  # 创建日志文件夹
    logger.add(log_file)
