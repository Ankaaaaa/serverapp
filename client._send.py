"""Программа-клиент"""

import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT
from common.utils import get_message, send_message
import argparse
import logging
from errors import ReqFieldMissingError, ServerError
from decorated import log
import logs.config_client_log

CLIENT_LOGGER = logging.getLogger('client')

@log
def get_message_from_other(message):
    """чтение сообщений от пользователей"""
    if ACTION in message and message[ACTION] == MESSAGE and \
        SENDER in message and MESSAGE_TEXT in message:
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Сообщение не содержит необходимых данных{message}')

@log
def create_message(sock, account_name='Guest'):
    """Поллачем при воде сообщение с консоли"""
    message = input('Ввведите сообщение или введите "exit" для выхода ')
    if message == 'exit':
        sock.close()
        CLIENT_LOGGER.info(f'Пользователь завершил работу')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Создано сообщение {message_dict}')
    return message_dict

@log
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
    CLIENT_LOGGER.debug(f'Создано сообщение: {out} для пользователя {account_name}')
    return out

@log
def read_answer(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    CLIENT_LOGGER.debug(f'Чтение сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOGGER.info('Cообщение от сервера прочитано успешно')
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)

@log
def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    return parser


def main():
    '''Загружаем параметы коммандной строки'''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical('Ошибка в номере порта: ',  server_port)
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_mode}')


    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, say_hello())
        read_answer(get_message(transport))
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical('Не удалось подключится к серверу')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error('В ответе от сервера отсутствует необходимое поле', missing_error.missing_field)
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)

    if client_mode == 'send':
        print('Режим работы: отправка сообщений ')
    else:
        print('Режим работы: прием сообщений ')
    while True:
        if client_mode == 'send':
            try:
                send_message(transport, create_message(transport))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)
        if client_mode == 'listen':
            try:
                get_message_from_other(get_message(transport))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)



if __name__ == '__main__':
    main()
