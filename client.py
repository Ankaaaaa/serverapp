"""Программа-клиент"""

import sys
import json
import socket
import time
from common.variables import *
from common.utils import get_message, send_message
import argparse
import logging
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from decorated import log
import logs.config_client_log
import threading
import dis
from metaclasses import ClientMaker


CLIENT_LOGGER = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()


    def create_message_exit(self):
        """создаем сообщение о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
            }

    def create_message(self):
        """Поллачем при воде сообщение с консоли"""
        to_user = input('Введите кому хотите отправить сообщение: ')
        message = input('Ввведите сообщение: ')

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Создано сообщение {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Сформирован словарь сообщения для пользователя  {to_user}')
        except:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером')
            exit(1)


    def user_community(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду для дальнейших действий: ')
            if command == 'm':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_message_exit())
                except:
                    pass
                print('Пользователь покинул чат')
                CLIENT_LOGGER.info(f'Пользователь завершил работу')
                time.sleep(1)
                break
            else:
                print('Проверьте вводимую команду или введите help ')

    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('m - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


# Класс-приём сообщений с сервера. Принимает сообщения, выводит в консоль
class ClientReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()


    def get_message_from_other(self):
        """чтение сообщений от пользователей через сервер"""
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
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
def say_hello(account_name):
    '''
    Функция генерирует запрос о присутствии клиента
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
    '''
    CLIENT_LOGGER.debug(f'Чтение сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOGGER.info('Cообщение от сервера прочитано успешно')
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)

@log
def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
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
        exit(1)

    """Сообщаем о запуске"""
    print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')

    # при отсутсвии имени пользователя, запрашиваем еще раз
    if not client_name:
        client_name = input(f'Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, пользователь: {client_name}')


    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, say_hello(client_name))
        answer = read_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером: {answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical('Не удалось подключится к серверу')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error('В ответе от сервера отсутствует необходимое поле', missing_error.missing_field)
        exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)


    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиенский процесс приёма сообщний
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.get_message_from_other()

        # запускаем отправку сообщений и взаимодействие с пользователем.
        user_comm = ClientSender(client_name, transport)
        user_comm.daemon = True
        user_comm.user_community()
        CLIENT_LOGGER.debug('Запущены процессы')


        while True:
            time.sleep(2)
            if receiver.is_alive() and user_comm.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
