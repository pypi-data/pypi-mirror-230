import os
import datetime
import sys
from loguru import logger


# 在需要的地方使用executable_dir


def is_executable():
    # 判断是否通过可执行文件执行
    return getattr(sys, "frozen", False) or hasattr(sys, "real_prefix")


def setup_logger():
    # 获取当前程序所在的目录路径
    if is_executable():
        # 获取可执行文件的路径
        executable_path = sys.executable
        # 获取可执行文件所在的目录路径
        current_dir = os.path.dirname(os.path.abspath(executable_path))
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    logger.debug(f"current_dir:{current_dir}")
    # 创建日志文件夹
    log_dir = os.path.join(current_dir, "log")
    os.makedirs(log_dir, exist_ok=True)

    # 指定日志文件的路径和配置
    log_file = os.path.join(log_dir, f"{datetime.date.today()}.log")
    logger.add(log_file)
