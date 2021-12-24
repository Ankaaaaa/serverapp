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
from errors import IncorrectDataRecivedError
from descriptrs import Port
from metaclasses import ServerMaker



# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


# Основной класс сервера
class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        # Параметры подключения
        self.listen_address = listen_address
        self.listen_port = listen_port

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()


    def init_socket(self):
        SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {self.listen_port}, '
                           f'адрес с которого принимаются подключения: {self.listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')

        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind(( self.listen_address,  self.listen_port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        # Инициализация Сокета
        self.init_socket()
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.read_news(get_message(client_with_message), client_with_message, clients, names)
                    except Exception:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                           f'отключился от сервера.')
                        # удаляем клиента который отключился
                        self.clients.remove(client_with_message)

                # Если есть сообщения для отправки, обрабатываем каждое
                for mes in self.messages:
                    try:
                        self.process_message(mes, send_data_lst)
                    except Exception:
                        SERVER_LOGGER.info(f'Клиент {mes[DESTINATION]} отключился от сервера.')
                        self.clients.remove(mes[DESTINATION])
                        del self.names[mes[DESTINATION]]
                self.messages.clear()

        # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
        # пользователей и слушающие сокеты. Ничего не возвращает.
    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(
                f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def read_news(self, message, client):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента
        '''
        SERVER_LOGGER.debug(f'Получено сообщение от клиента {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            # если такой пользователь еще не зарегистрирован
            # регистрируем, иначе отправляем ответ и завершаем соединение
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Такое имя уже существует'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message and MESSAGE_TEXT in message and \
                SENDER in message:
            self.messages_list.append(message)
            return
        # если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and \
            ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректный'
            send_message(client, response)
            return



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



    server = Server(listen_address, listen_port)
    server.main_loop()



if __name__ == '__main__':
    main()
