import logging

SERVER_LOGGER = logging.getLogger('server')

# Дескриптор для описания порта:
class Port:
    def __set__(self, instance, listen_port):
        if listen_port < 1024 or listen_port > 65535:
            SERVER_LOGGER.critical(f'Ошибка в номере порта: {listen_port}')
            exit(1)
        # Если порт прошёл проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = listen_port

    def __set_name__(self, owner, name):
        self.name = name

