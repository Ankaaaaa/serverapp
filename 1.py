def converter(my_list):
    new_list = []
    for i in my_list:
        print(f'тип данных: {i} - {type(i)}')
        new_list.append(i.encode('utf-8'))
    for j in new_list:
        print(f'тип данных: {j} - {type(j)}')
    return new_list

my_list = ['разработка', 'сокет', 'декоратор']

converter(my_list)

