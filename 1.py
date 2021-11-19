"""
Задание на закрепление знаний по модулю CSV.
Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
и формирующий новый «отчетный» файл в формате CSV
"""
import chardet
import re
import csv

def get_data(file_lst):
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]

    for file in file_lst:
        # определяем кодировку
        with open(file, 'rb') as my_file:
            CONTENT = my_file.read()
        ENCODING = chardet.detect(CONTENT)['encoding']
        print(ENCODING)
        # считываем файл с правильной кодировкой и ищем нужные строки с данными
        with open(file, 'r', encoding=ENCODING) as my_file:
            TEXT = my_file.readlines()
            for i in TEXT:
                if re.match('Изготовитель системы', i):
                    os_prod_list.append(re.search(r'(Изготовитель системы).\s*(.*)', i).group(2))
                elif re.match('Название ОС', i):
                    os_name_list.append(re.search(r'(Название ОС).\s*(.*)', i).group(2))
                elif re.match('Код продукта', i):
                    os_code_list.append(re.search(r'(Код продукта).\s*(.*)', i).group(2))
                elif re.match('Тип системы', i):
                    os_type_list.append(re.search(r'(Тип системы).\s*(.*)', i).group(2))
    # создаем общий список
    for i in range(len(file_lst)):
        main_data.append([
            os_prod_list[i],
            os_name_list[i],
            os_code_list[i],
            os_type_list[i]
        ])
    return main_data

main_data = get_data(['info_1.txt', 'info_2.txt', 'info_3.txt'])

def  write_to_csv(main_data):
    with open('write.csv', 'w') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in main_data:
            f_n_writer.writerow(row)

    with open('write.csv') as f_n:
        print(f_n.read())

write_to_csv(main_data)



