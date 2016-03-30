__author__ = "gambrinius"


def get_int_list(input_str):
    if isinstance(input_str, str):
        int_list = list()
        if input_str != '':

            split_str = input_str.split(',')
            for i in split_str:
                int_list.append(int(i))

            # print("Created integer list", int_list)

            return int_list
        else:
            # print("Input string is empty, created empty list", int_list)
            return int_list
    else:
        # print("Input data isn't string type")
        pass


def str_from_int_list(int_list):
    if isinstance(int_list, list):
        string_list = list()

        for i in int_list:
            string_list.append(str(i))

        output_str = ','.join(string_list)
        # print("Created string list", output_str)

        return output_str
    else:
        pass


def add_to_str(source_string, added_str):
    if isinstance(added_str, str):
        if isinstance(source_string, str):

            if source_string != '':
                output_str = source_string + ',' + added_str
            else:
                output_str = added_str

            # print("New string with added str", output_str)
            return output_str
        else:
            pass
    else:
        pass

"""
string = "1,3,5,7,8,88,99,100"
test_string = "99"
print("Source string", string)
get_int_list(string)

lst = [2, 3, 4, 6, 7]
str_from_list(lst)

add_to_str('9', string)

if test_string in string:
    print("%s found in source string" % test_string)
else:
    print("Not found in string")
"""

"""
get_int_list(str())
string = str()
string = str_from_int_list(list())
print("Empty string", string)
print("Empty list ", get_int_list(string))
"""