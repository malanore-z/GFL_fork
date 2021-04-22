import logging.config

# 需要使用日志模块logging之前，加载配置文件，创建logger
# 加载配置文件
logging.config.fileConfig('/Users/YY/PycharmProjects/GFL_fork/gfl/log/Logging.conf')
# 创建 logger
logger = logging.getLogger('node_logger')


def test():
    logger.debug('node:debug message')
    logger.info('node:info message')
    logger.warning('node:warn message')
    logger.error('node:error message')


if __name__ == '__main__':
    test()