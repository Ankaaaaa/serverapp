"""Программа-клиент"""

import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message
import argparse
import logging
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from decorated import log
import logs.config_client_log
import threading

CLIENT_LOGGER = logging.getLogger('client')

@log
def create_message_exit(account_name):
    """создаем сообщение о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
        }


@log
def get_message_from_other(sock, my_username):
    """чтение сообщений от пользователей через сервер"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                SENDER in message and MESSAGE_TEXT in message and MESSAGE_TEXT in message and \
                message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Сообщение не содержит необходимых данных{message}')
        except IncorrectDataRecivedError:
                CLIENT_LOGGER.error(f'не удалось декодировать сообщение')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical('fПотеряно соединение с севрером')
            break

@log
def create_message(sock, account_name='Guest'):
    """Поллачем при воде сообщение с консоли"""
    to_user = input('Введите кому хотите отправить сообщение: ')
    message = input('Ввведите сообщение: ')

    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Создано сообщение {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Сформирован словарь сообщения для пользователя  {to_user}')
    except:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером')
        sys.exit(1)


@log
def user_community(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду для дальнейших действий: ')
        if command == 'm':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_message_exit(username))
            print('Пользователь покинул чат')
            CLIENT_LOGGER.info(f'Пользователь завершил работу')
            time.sleep(1)
            break
        else:
            print('Проверьте вводимую команду или введите help ')


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('m - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def say_hello(account_name):
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
    # parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    return parser


def main():
    '''Загружаем параметы коммандной строки'''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical('Ошибка в номере порта: ',  server_port)
        sys.exit(1)

    """Сообщаем о запуске"""
    print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')

    # при отсутсвии имени пользователя, запрашиваем еще раз
    if not client_name:
        client_name = input(f'Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, пользователь: {client_name}')


    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, say_hello(client_name))
        read_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical('Не удалось подключится к серверу')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error('В ответе от сервера отсутствует необходимое поле', missing_error.missing_field)
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)


    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(target=get_message_from_other, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_comm = threading.Thread(target=user_community, args=(transport, client_name))
        user_comm.daemon = True
        user_comm.start()
        CLIENT_LOGGER.debug('Запущены процессы')


        while True:
            time.sleep(2)
            if receiver.is_alive() and user_comm.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
