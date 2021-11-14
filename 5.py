import subprocess
import chardet

web = ['youtube.com', 'yandex.ru']
for i in web:
    args = ['ping', '-n', '4', i]
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        result = chardet.detect(line)
        print(result)
        line = line.decode(result['encoding']).encode('utf-8')
        print(i,  line.decode('utf-8'))