import sys
from loguru import logger


def is_executable():
    # 判断是否通过可执行文件执行
    return getattr(sys, "frozen", False) or hasattr(sys, "real_prefix")


def getCurrentDir():
    import os

    # 获取当前程序所在的目录路径
    if is_executable():
        # 获取可执行文件的路径
        executable_path = sys.executable
        # 获取可执行文件所在的目录路径
        current_dir = os.path.dirname(os.path.abspath(executable_path))
    else:
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        # current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"当前目录:{current_dir}")
    return current_dir


def getToday():
    import datetime

    return datetime.date.today().strftime("%Y-%m-%d")


def mkdir(filepath):
    # 获取目录路径
    import os

    directory = os.path.dirname(filepath)
    os.makedirs(directory, exist_ok=True)


def getLogfile(dir, format):
    import os

    current_dir = getCurrentDir()
    log_dir = os.path.join(current_dir, dir)
    log_dir = os.path.join(log_dir, getToday())
    log_file = os.path.join(log_dir, format)
    mkdir(log_file)  # 创建日志文件夹
    return log_file
