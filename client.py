"""Программа-клиент"""

import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message
import argparse
import logging
from errors import ReqFieldMissingError


CLIENT_LOGGER = logging.getLogger('client')

def say_hello(account_name='Guest'):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    '''
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug('Создано сообщение:', out)
    return out


def read_answer(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    CLIENT_LOGGER.debug('Чтение сообщения от сервера:', message)
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOGGER.info('Cообщение от сервера прочитано успешно:')
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    return parser


def main():
    '''Загружаем параметы коммандной строки'''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical('Ошибка в номере порта: ',  server_port)
        sys.exit(1)


    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = say_hello()
        send_message(transport, message_to_server)
        read_answer(get_message(transport))
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical('Не удалось подключится к серверу')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error('В ответе от сервера отсутствует необходимое поле', missing_error.missing_field)



if __name__ == '__main__':
    main()
