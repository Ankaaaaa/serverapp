my_list = ['class', 'function', 'method']

def conventer(my_list):
    for i in my_list:
        DEC_STR = eval(f'b"{i}"')
        print(f'для {DEC_STR} тип данных {type(DEC_STR)} длинна {len(DEC_STR)}')


conventer(my_list)