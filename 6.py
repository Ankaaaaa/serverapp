import chardet

my_list = ['сетевое программирование', 'сокет', 'декоратор']

# создаем файл, делаем запись
my_file = open("test_file.txt", 'w', encoding='utf-8')
for i in my_list:
    my_file.write(str(i) + '\n')
print(type(my_file))
my_file.close()


# открываем файл, выводим содержимое файла
my_file = open("test_file.txt", 'r', encoding='utf-8')
for i in my_file:
    print(i)
my_file.close()


# опеределяем кодировку файла
with open('test_file.txt', 'rb') as f:
    result = chardet.detect(f.read())
    print('кодировка файла ', result)