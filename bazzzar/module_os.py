import os

__author__ = 'gambrinius'

print(os.getcwd())
print(os.uname())
# os.makedirs('00//00//00//11//33//')


def get_path(id_profile):
    path = str()
    string = str(id_profile)
    while len(string) != 10:
        string = '0' + string

    str_list = list(string)

    for i in range(0, 10):
        if i % 2 != 0:
            path += str_list[i] + '//'
        else:
            path += str_list[i]

    return path

print(get_path(123))

try:
    os.makedirs(get_path(1122))
except FileExistsError:
    print('Folder already exist')  # pass
