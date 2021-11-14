my_list = ['attribute', 'класс', 'функция', 'type']

def check(my_list):
    for word in my_list:
        for letter in word:
            if ord(letter) > 127:
                print(f'{word} - это слово нельзя записать в байтовом ввиде ')
                break




check(my_list)