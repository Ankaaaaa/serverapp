import logging
import sys
import logs.config_server_log
import logs.config_client_log
import inspect
import functools

# определяем кто вызвает
if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    """Декоратор"""
    # @functools.wraps(func)
    def save(*args, **kwargs):
        save_func = func(*args, **kwargs)
        LOGGER.debug(f'Функция {func.__name__} c параметрами {args}, {kwargs} - '
                     f'была вызвана из модуля {inspect.stack()[1][3]}')
        return save_func
    return save



