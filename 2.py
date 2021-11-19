"""
Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными
"""

import json

def write_order_to_json(list):
    for ls in list:
        order = {}
        heading = ['item', 'quantity', 'price', 'buyer', 'date']
        for index, value in enumerate(zip(heading, ls)):
            dict = value[0]
            dictionary = value[1]
            order[dict] = dictionary
        print(order)

        with open('write.json', 'a', encoding='utf-8') as f_n:
            json.dump(order, f_n, ensure_ascii=False, indent=4)
            f_n.write(',\n')

#
my_list = [['монитор', 12, 5400, 'мвидео', '12.07.2021'],
           ['клавиатура', 25, 400, 'эльдорадо', '02.12.2021'],
           ['принтер', 7, 14000, 'технопарк', '15.10.2021']]

write_order_to_json(my_list)

with open('write.json') as f_n:
    print(f_n.read())