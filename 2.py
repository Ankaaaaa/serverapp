import ipaddress

from tabulate import tabulate


def host_range_ping():
    list_result = {}
    ip_change = input('введите количество перебора: ')
    IP1 = ipaddress.ip_address('192.168.1.250')
    for i in range(int(ip_change)):
        j = (IP1 + i)
        last_o = str(j).split('.')
        if int(last_o[3]) < 255:
            try:
                ipaddress.ip_network(j)
                list_result.setdefault('доступен', []).append(j)
            except ValueError:
                list_result.setdefault('недоступен', []).append(j)
        else:
            list_result.setdefault('недоступен', []).append(j)
    # print(tabulate(list_result, headers='keys', stralign="center", tablefmt="grid"))
    return list_result



def host_range_ping_tab(func):
    print(tabulate(func, headers='keys', stralign="center", tablefmt="grid"))


host_range_ping_tab(host_range_ping())
