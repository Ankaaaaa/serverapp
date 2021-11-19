"""
Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата
"""

import yaml

my_dict = {'комплектация': ['монитор', 'блок', 'клавиатура'],
           'цена$': 8000,
           'производитель': {
                'страна': ['china', 'usa'],
                'год': 2008}
                }

def write_dict_to_yaml(my_dict):
    with open('write.yaml', 'w', encoding='utf-8') as f_n:
        # yaml.dump(DATA_TO_YAML, f_n, default_flow_style=False)
        yaml.dump(my_dict, f_n, default_flow_style=False, allow_unicode=True)

    with open('write.yaml', encoding='utf-8') as f_n:
        F_N_CONTENT = yaml.load(f_n, Loader=yaml.FullLoader)
        print(F_N_CONTENT)


write_dict_to_yaml(my_dict)
