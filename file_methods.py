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


# write parts of temporary file-objects to new file
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
    size_set = {'_S': (128, 128), '_M': (256, 256), '_L': (512, 512)}
    for size in size_set:
        try:
            f, e = os.path.splitext(infile_path)    # f - part before '.', e - part after '.'
            img = Image.open(infile_path)
            img.thumbnail(size_set[size])   # resize image

            full_name = f + size + '.jpg'
            img.save(full_name, "JPEG")
        except IOError:
            pass
