"""Кофнфиг серверного логгера"""

import sys
import os
import logging
import logging.handlers

sys.path.append('../')
from common.variables import LOGGING_LEVEL, SERVER_FORMATTER_TYPE

# создаём формировщик логов (formatter):
# --------------------добавила переменную, которая будет содержать формат сообщений в файл varibales
SERVER_FORMATTER = logging.Formatter(SERVER_FORMATTER_TYPE)

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# создаём потоки вывода логов (ежедневная ротация файлов)
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='S')
LOG_FILE.setFormatter(SERVER_FORMATTER)


# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('server')
LOGGER.addHandler(LOG_FILE)
LOGGER.addHandler(STREAM_HANDLER)
#---------- устанавливаем уровень с которого будут выводится сообщения
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
