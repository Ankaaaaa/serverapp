my_list = ['разработка', 'администрирование', 'protocol', 'standard']

def conventer (my_list):
    new_list_bytes = []
    for i in my_list:
        new_list_bytes.append(i.encode('utf-8'))
    print(new_list_bytes)
    new_list_str = []
    for j in new_list_bytes:
        new_list_str.append(j.decode('utf-8'))
    print(new_list_str)



conventer(my_list)