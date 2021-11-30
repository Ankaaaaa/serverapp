"""Программа-сервер"""

import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_message, send_message
import argparse
import logging
import logs.config_server_log
from errors import IncorrectDataRecivedError


# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')

def read_news(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    :param message:
    :return:
    '''
    SERVER_LOGGER.debug(f'Получено сообщение от клиента {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        SERVER_LOGGER.info('Cообщение от клиента  прочитано успешно')
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    # проверка получения корретного номера порта для работы сервера.
    if listen_port < 1024 or listen_port > 65535:
        SERVER_LOGGER.critical('Ошибка в номере порта: ',  listen_port)
        sys.exit(1)
    else:
        SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                           f'адрес с которого принимаются подключения: {listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # Слушаем порт

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
        try:
            message_from_client = get_message(client)
            response = read_news(message_from_client)
            SERVER_LOGGER.info(f'Сформирован ответ клиенту {response}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Соединение с клиентом закрывается {client_address}')
            client.close()
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Не возможно декодировать сообщение от клиента {client_address}. Соединение закрыто')
            client.close()
        except IncorrectDataRecivedError:
            SERVER_LOGGER.error(f'Принято некорретное сообщение от клиента {client_address}. Соединение закрыто.')
            client.close()


if __name__ == '__main__':
    main()
