import os
from bazzzar.settings import MEDIA_ROOT
from PIL import Image

__author__ = 'gambrinius'


# final_path to dir for profile
def get_path(id_profile):
    path = str()
    string = str(id_profile)
    while len(string) != 10:
        string = '0' + string

    str_list = list(string)

    for i in range(0, 10):
        if i % 2 != 0:
            path += str_list[i] + '/'
        else:
            path += str_list[i]

    final_path = MEDIA_ROOT + "/" + path
    return final_path


# write part of temporary file-objects to new file
def handle_uploaded_file(f, path):
    with open(path, 'wb+') as uploaded_file:
        for chunk in f.chunks():
            uploaded_file.write(chunk)


# Image convert to JPG, return full_path and filename
def convert_to_jpg(infile_path):
    f, e = os.path.splitext(infile_path)

    outfile = f + ".jpg"
    Image.open(infile_path).save(outfile)
    os.remove(infile_path)

    return outfile[-12:]


# Image resize to S,M,L sizes
def image_resize(infile_path):
    size_set = {'S': (128, 128), 'M': (256, 256), 'L': (512, 512)}
    for size in size_set:
        postfix = ''
        if size == 'S':
            postfix = '_S'
        if size == 'M':
            postfix = '_M'
        if size == 'L':
            postfix = '_L'
        try:
            f, e = os.path.splitext(infile_path)
            # print(f, e)
            img = Image.open(infile_path)
            # print(size_set[size])
            img.thumbnail(size_set[size])
            full_name = f + postfix + '.jpg'
            # print(full_name)
            img.save(full_name, "JPEG")
        except IOError:
            pass
