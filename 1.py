import locale
import ipaddress
import subprocess
import socket
from pprint import pprint

from tabulate import tabulate


def host_ping(web):
    list_result = {}
    list_ip = []
    for i in web:
        for char in i:
            if char.isalpha() == True:
                args = ['ping', '-n', '4', i]
                subproc_ping = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                code = subproc_ping.wait()
                if code == 0:
                    list_ip.append(socket.gethostbyname(i))
                    list_result.setdefault('доступен', []).append(i)
                    # list_result.append({[i] = ' доступен'})
                else:
                    list_result.setdefault('недоступен', []).append(i)

                break
            else:
                try:
                    ipaddress.ip_network(i)
                    list_ip.append(i)
                    list_result.setdefault('доступен', []).append(i)
                    break
                except ValueError:
                    list_result.setdefault('недоступен', []).append(i)
                    break
    print(tabulate(list_result, headers='keys', stralign="center", tablefmt="grid"))
    return list_result,  list_ip


web = ['youtube.com', 'yandex.ru', 'yanderu', '10.0.1.1/24', '10.0.1.0/24']
host_ping(web)
