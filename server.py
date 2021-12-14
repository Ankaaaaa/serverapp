"""Программа-сервер"""
import select
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, \
    EXIT
from common.utils import get_message, send_message
import argparse
import logging
from decorated import log
import logs.config_server_log



# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')

@log
def read_news(message, messages_list, client, clients, names):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    :param message:
    :return:
    '''
    SERVER_LOGGER.debug(f'Получено сообщение от клиента {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        # если такой пользователь еще не зарегистрирован
        # регистрируем, иначе отправляем ответ и завершаем соединение
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Такое имя уже существует'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений.
    # Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
        DESTINATION in message and TIME in message and MESSAGE_TEXT in message and \
            SENDER in message:
        messages_list.append(message)
        return
    # если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and \
        ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректный'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает."""
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю - {message[DESTINATION]} от пользователя -{message[SENDER]}')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise  ConnectionError
    else:
        SERVER_LOGGER.error(f'Потльзователь {message[DESTINATION]} не зарегистрирован на сервере,'
        f'не возможно отпраивть сообщение')


@log
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
        SERVER_LOGGER.critical(f'Ошибка в номере порта: {listen_port}')
        sys.exit(1)
    else:
        SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                           f'адрес с которого принимаются подключения: {listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    # список клиентов , очередь сообщений
    clients = []
    messages = []
    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()
    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    read_news(get_message(client_with_message), messages, client_with_message, clients, names)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    # удаляем клиента который отключился
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки, обрабатываем каждое
            for mes in messages:
                try:
                    process_message(mes, names, send_data_lst)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {mes[DESTINATION]} отключился от сервера.')
                    clients.remove(mes[DESTINATION])
            messages.clear()



if __name__ == '__main__':
    main()
