import logging
import os
import gzip
from logging.handlers import TimedRotatingFileHandler
import datetime

LOG_FILE_PATH = "logs/xtools"


def setup_logger():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # 获取今天的日期
    today = datetime.date.today()

    # 格式化日期为年月日
    date_str = today.strftime('%Y-%m-%d')
    file_name = f"{LOG_FILE_PATH}_{date_str}.log"
    directory = os.path.dirname(file_name)
    os.makedirs(directory, exist_ok=True)
    # 创建TimedRotatingFileHandler，每日生成一个日志文件
    handler = TimedRotatingFileHandler(file_name, when='midnight', interval=1, backupCount=7, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def compress_log():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    log_filename = f'{LOG_FILE_PATH}_{yesterday.strftime("%Y-%m-%d")}.log'
    if not os.path.exists(log_filename):
        return ""
    with open(log_filename, 'rb') as f_in:
        with gzip.open(f'{log_filename}.gz', 'wb') as f_out:
            f_out.writelines(f_in)
    os.remove(log_filename)


logger = setup_logger()

if __name__ == '__main__':
    logger = setup_logger()

    # 产生一些日志
    for i in range(10):
        logger.debug('This is a debug message %d', i)

    # 压缩昨天的日志文件
    compress_log()
