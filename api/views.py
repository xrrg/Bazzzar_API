# -*- coding: utf-8 -*
import uuid
import hashlib

from smtplib import SMTPException

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render

from .models import *
from django.contrib import auth

import sqlite3
from parsing_string import *
from file_methods import *


def initialize(request):  # load main.html
    context = dict()
    return render(request, '', context)


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        new_user = User.objects.create_user(username=username, password=password, email=email)
        new_user.save()
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        salted_username = salt + new_user.username
        token = hashlib.sha1(salted_username.encode('utf-8')).hexdigest()  # TODO: add confirmation email
        # СТРАНННО ЧТО token = activation_key !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        new_profile = Profile(user=new_user, token=token,
                              activation_key=token)
        new_profile.save()

        return JsonResponse({"status": "successful user registration", "token": token})
    else:
        return JsonResponse({"status": "error"})


def auth_check(request):
    """
    Correct input and permissions check. Returns user profile in case of success
    as dictionary and returns int '1' in case of failing, and int '2' in case of
    wrong token.
    """

    user = auth.get_user(request)
    request_token = request.POST['token']

    if user.is_authenticated() and request_token != '':
        try:
            user_profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            return 1
        else:
            if user_profile.token == request_token:
                return user_profile
    return 1


def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)

            return JsonResponse({"status": "successful log in"})
        else:
            return JsonResponse({"status": "authentication error"})
    else:
        return JsonResponse({"status": "error"})


def log_out(request):
    if request.method == 'GET':
        user = auth.get_user(request)
        if user:
            auth.logout(request)

            return JsonResponse({"status": "successful log out"})
    else:
        return JsonResponse({"status": "error"})


def change_email(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            new_email = request.POST['new_email']
            user_profile.user.email = new_email
            user_profile.user.save()
            return JsonResponse({'status': 'e-mail successful changed'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def change_password(request):  # mobile client handles old password check
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            new_password = request.POST['new_password']
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            return JsonResponse({'status': 'password successful changed'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def reset_password(request):
    if request.method == 'POST':
        user_login = request.POST['login']
        user = User.objects.get(username=user_login)
        new_password = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:8]
        user.set_password(new_password)
        user.save()
        email_subject = 'Password reset'
        email_body = "Dear %s, your new password is %s." % (user.username, new_password)
        try:
            send_mail(email_subject, email_body, 'email@email', [user.email], fail_silently=False)
        except SMTPException:
            return JsonResponse({'status': 'smtp_exception'})

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовый вариант. будь осторожен, путник
def insert_row(request):
    profile_list = list()
    user = User.objects.get(id=3)   # can delete list of records

    # for user in users:
    profile_list.append(user.id)    # добавление записи в список, для последующей передачи

    category = Category.objects.get(name='LOL')
    category.insert_row(profile_list=profile_list)

    return JsonResponse({'status': 'successfully add row'})


def add_subscription(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            category_id = request.POST['category_id']
            try:
                category = Category.objects.get(id=category_id)

                if category:
                    try:
                        profile_list = list()
                        profile_list.append(user_profile.id)
                        category.insert_row(profile_list=profile_list)

                        return JsonResponse({'status': 'subscription successful add'})

                    except sqlite3.DatabaseError or sqlite3.DataError:
                        return JsonResponse({'status': 'database error or data error'})

            except ObjectDoesNotExist:
                return JsonResponse({'status': "category doesn't exist"})

        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовый вариант. будь осторожен, путник
def delete_row(request):
    profile_list = list()
    user = User.objects.get(id=3)   # can delete list of users

    # for user in users:
    profile_list.append(user.id)    # добавление записи в список, для последующей передачи

    category = Category.objects.get(name='LOL')
    category.delete_row(profile_list=profile_list)

    return JsonResponse({'status': 'successfully delete row'})


def delete_subscription(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            category_id = request.POST['category_id']
            category = Category.objects.get(id=category_id)

            if category:
                try:
                    profile_list = list()
                    profile_list.append(user_profile.id)
                    category.delete_row(profile_list=profile_list)

                    return JsonResponse({'status': 'subscription successful delete'})

                except sqlite3.DatabaseError or sqlite3.DataError:
                    return JsonResponse({'status': 'database error or data error'})
            else:
                return JsonResponse({'status': "category doesn't exist "})

        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовый вариант. будь осторожен, путник
def add_category(request):
    Category(name='#').save()

    return JsonResponse({'status': 'successfully added'})


# тестовый вариант. будь осторожен, путник
def delete_category(request):
    Category.objects.get(name='#').delete()

    return JsonResponse({'status': 'successfully deleted'})


def add_favorite(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = str(request.POST['advertisement_id'])
            if adv_id in user_profile.userFavorites:
                return JsonResponse({'status': 'advertisement_id already exist in userFavorites'})
            else:
                user_profile.userFavorites = add_to_str(user_profile.userFavorites, adv_id)  # '1,2,4' + ',' + '7'
                # or only '7' if source string is empty
                user_profile.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def delete_favorite(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = int(request.POST['advertisement_id'])
            int_list = get_int_list(user_profile.userFavorites)  # get int list of id advertisements
            if adv_id in int_list:
                int_list.remove(adv_id)
                user_profile.userFavorites = str_from_int_list(int_list)
                user_profile.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': "not found advertisement or user favorites string empty"})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def get_categories(request):
    """
    Function return data with existing categories (id, name) in json-format
    :param request: user token
    :return: json dictionary
    """
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            json_dict = dict()
            json_dict['table'] = 'categories'
            category_records = Category.objects.all()
            json_dict['records_number'] = len(category_records)

            records_dict = dict()
            for i in range(0, len(category_records)):
                records_dict[i+1] = {
                    'id': category_records[i].pk,
                    'name': category_records[i].name,
                }
            json_dict['records'] = records_dict
            return JsonResponse(json_dict)
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def get_advs_by_id(request):
    """
    Function return data with existing categories (id, name) in json-format
    :param request: user token, list of ids Advertisement objects
    :return:json objects
    """
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            id_str = request.POST['id']
            id_list = get_int_list(id_str)
            json_dict = dict()
            json_dict['table'] = 'advertisements_by_ids'
            not_found_records_list = []
            records = dict()
            i = 1
            for x in id_list:
                try:
                    record = Advertisement.objects.get(pk=x)
                except ObjectDoesNotExist:
                    not_found_records_list.append(x)
                    continue
                records[i] = {
                    'profile':  record.profile.user.username,
                    'category':  record.category.name,
                    'city':  record.city.name,
                    'title': record.title,
                    'description': record.description,
                    'condition': str(record.condition),
                    'phone': record.phone
                }
                i += 1
            json_dict['records'] = records
            json_dict['id_not_found'] = not_found_records_list
            return JsonResponse(json_dict)
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def get_str_params(request, str_list):
    """
    Function get required str parameters from POST method
    :param request:
    :param str_list: list of keys, needs to get values from body of POST method.
    :return: kwargs - dict of string parameters
    """
    kwargs = dict()
    for name in str_list:
        if request.POST[name] != '':
            kwargs[name] = request.POST[name]

    return kwargs


def get_int_params(request, str_list):
    """
    Function get required int parameters from POST method
    :param request:
    :param str_list: list of keys, needs to get values from body of POST method.
    :return: kwargs - dict of integer parameters.
    """
    kwargs = dict()
    for name in str_list:
        if request.POST[name] != '':
            if isinstance(int(request.POST[name]), int):
                kwargs[name] = int(request.POST[name])

    return kwargs


def base_filter(request):  # add contains filter to title
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'condition', 'price']
        str_filters = ['title__contains']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def house_filter(request):  # maybe category = 'House' by default
    """
    Function filter Advertisement Objects (Houses) by parameters gotten from POST request  and return them.
    :param request:
    :return: json descriptions of house objects
    """
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'price']
        str_filters = ['title__contains', 'housing__communications__contains', 'housing__area']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
                return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def transport_filter(request):  # maybe category = 'Auto' by default
    """
    Function filter Advertisement Objects (Auto, Motorcycles, Bicycles)
    by parameters gotten from POST request  and return them.
    :param request:
    :return: json descriptions of house objects
    """
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'price', 'transport__year', 'transport__motor_power']
        str_filters = ['title__contains', 'transport__color__contains']
        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def clothes_filter(request):
    """
    Function filter Advertisement Objects (Clothes)
    by parameters gotten from POST request  and return them.
    :param request:
    :return: json descriptions of house objects
    """
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'price', 'clothes__sex']
        str_filters = ['title__contains']
        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def kidsthings_filter(request):
    """
    Function filter Advertisement Objects (Kids Things)
    by parameters gotten from POST request  and return them.
    :param request:
    :return: json descriptions of house objects
    """
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'price', 'kids_things__sex', 'kids_things__age']
        str_filters = ['title__contains']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def tourism_filter(request):
    """
    Function filter Advertisement Objects (Tourism)
    by parameters gotten from POST request  and return them.
    :param request:
    :return: json descriptions of house objects
    """
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'price']
        str_filters = ['title__contains', 'recreation__name__contains']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))

            advs = Advertisement.objects.filter(**params)
            """
            доделать отправление обьектов-обьявлений в json формате на мобильный клиент
            """
            advs_list = list()
            for adv in advs:
                advs_list.append(adv.title)

            return JsonResponse({'status': 'success', 'values': advs_list})

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def add_adv(request):
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            params = dict()
            int_args = ['condition', 'price']
            str_args = ['title', 'description', 'phone']

            try:
                params['profile'] = user_profile

                if request.POST['category'] != '':
                    if isinstance(int(request.POST['category']), int):
                        params['category'] = Category.objects.get(id=int(request.POST['category']))

                if request.POST['city'] != '':
                    if isinstance(int(request.POST['city']), int):
                        params['city'] = City.objects.get(id=int(request.POST['city']))

                params.update(get_int_params(request, int_args))
                params.update(get_str_params(request, str_args))

                advertisement = Advertisement.objects.create(**params)
                if advertisement:
                    advertisement.save()
                    advertisement.category.notification_counter += 1
                    advertisement.category.save()
                    return JsonResponse({'status': 'Advertisement successful add'})

            except Exception:
                return JsonResponse({'status': 'parameters_error'})

        else:
            return JsonResponse({'status': 'authentication_error or missing token'})
    else:
        return JsonResponse({'status': 'request_error'})


###############################################################################################
def del_adv(request):   # final version
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = request.POST['adv_id']
            try:
                adv = Advertisement.objects.get(pk=adv_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'advertisement not found'})
            except ValueError:
                return JsonResponse({'status': "adv_id value error"})
            else:
                if adv.profile.pk == user_profile.pk:
                    sizes = ('L', 'M', 'S')
                    image_list = adv.image_titles.split(',')
                    path = user_profile.folder_path

                    for image in image_list:
                        full_path = path + image
                        try:
                            os.remove(full_path)    # delete source image
                        except FileNotFoundError:
                            pass

                        for size in sizes:  # delete different sizes images
                            full_path = path + image[:8] + '_' + size + '.jpg'
                            try:
                                os.remove(full_path)
                            except FileNotFoundError:
                                pass

                    adv.delete()
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def edit_adv(request):  # changed by Vova
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = request.POST['adv_id']
            try:
                adv = Advertisement.objects.get(pk=adv_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'advertisement not found'})
            else:
                if adv.profile.pk == user_profile.pk:
                    params = request.POST.items()
                    payload = dict()
                    for x in params:
                        if x[1] != '':
                            payload[str(x[0])] = str(x[1])
                        else:
                            continue
                    arg_set = ('profile', 'title', 'description', 'condition', 'price', 'phone')
                    category_id = payload['category_id']
                    city_id = payload['city_id']
                    for arg in arg_set:
                        if arg in payload:
                            setattr(adv, arg, payload[arg])
                        else:
                            continue
                    if category_id != '':
                        try:
                            adv.category = Category.objects.get(pk=category_id)
                        except ObjectDoesNotExist:
                            return JsonResponse({'status': 'category not found'})
                    try:
                        if city_id != '':
                            adv.city = City.objects.get(pk=city_id)
                    except ObjectDoesNotExist:
                            return JsonResponse({'status': 'city not found'})
                    adv.save()
                    return JsonResponse({'status': 'success'})

                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def upload_photos(request):  # final version
    """
    Function processes the incoming images
    :param request: user token, advertisement id
    :return: status, list of failed upload files || (&&) list of success upload files
    """
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = request.POST['adv_id']
            try:    # check existence advertisement and belong to profile
                advertisement = Advertisement.objects.get(pk=adv_id, profile_id=user_profile.id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': "advertisement not found or doesn't belong by current user"})
            except ValueError:
                return JsonResponse({'status': "adv_id value error"})
            else:
                if user_profile.folder_path != '':  # check existence dir
                    dir_path = user_profile.folder_path
                else:
                    dir_path = get_path(user_profile.id)  # create dir-path for profile
                    try:
                        os.chdir(MEDIA_ROOT + "/")
                        os.makedirs(dir_path)   # create user's dir
                    except FileExistsError:
                        pass

                max_count = 5   # max photo count at 1 advertisement
                if advertisement.image_titles == '':  # current photo count at this advertisement
                    current_count = 0
                else:
                    current_count = len(advertisement.image_titles.split(','))

                if current_count < max_count:
                    success_upload = list()
                    failed_upload = list()

                    for fileName in request.FILES:
                        if current_count < max_count:
                            uploaded_file = request.FILES[fileName]  # object UploadedFile
                            image_format = uploaded_file.name[-4:]  # .jpg , .png , .bmp, etc.

                            image_name = str(uuid.uuid4())[:8] + image_format  # random filename with source format
                            full_path = dir_path + image_name

                            if image_format == '.jpg':
                                handle_uploaded_file(uploaded_file, full_path)  # save .jpg file
                                image_resize(full_path)  # resize image to S,M,L sizes
                                success_upload.append(image_name)

                                current_count += 1
                            else:
                                handle_uploaded_file(uploaded_file, full_path)  # save source format file

                                try:
                                    image_name = convert_to_jpg(full_path)  # create new file and remove source file
                                    success_upload.append(image_name)

                                    current_count += 1
                                except OSError:  # if not supported convert format
                                    failed_upload.append(uploaded_file.name)    # add failed filename
                                    os.remove(full_path)  # remove source file
                                    try:
                                        full_path = dir_path + image_name[:8] + '.jpg'
                                        os.remove(full_path)  # remove created file
                                    except FileNotFoundError:
                                        pass

                                    # return JsonResponse({'status': 'file_format_error'})

                                full_path = dir_path + image_name  # new full path
                                image_resize(full_path)  # resize image to S,M,L sizes
                        else:
                            break

                    images_str = ','.join(success_upload)  # save file names to Advertisement object
                    if advertisement.image_titles != '':
                        advertisement.image_titles += ',' + images_str
                    else:
                        advertisement.image_titles = images_str
                    advertisement.save()

                    user_profile.folder_path = dir_path  # save full path to  user folder
                    user_profile.save()
                    return JsonResponse({'status': 'successful upload',
                                         'success': success_upload,
                                         'failed': failed_upload})
                else:
                    return JsonResponse({'status': 'limit_error'})  # limit of 5 photos
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def delete_photos(request):  # final version
    """
    Function processes the incoming requests to delete photos
    :param request: user token, advertisement id, string of images names
    :return: json response
    """
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = request.POST['adv_id']
            try:    # check existence advertisement and belong to profile
                advertisement = Advertisement.objects.get(pk=adv_id, profile_id=user_profile.id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': "advertisement not found or doesn't belong by current user"})
            except ValueError:
                return JsonResponse({'status': "adv_id value error"})
            else:
                sizes = ('L', 'M', 'S')
                path = user_profile.folder_path
                image_list = request.POST['image_list'].split(',')  # values in request 'b8a5252f.jpg, .. ,9dc6bb03.jpg'
                for image in image_list:
                    if image in advertisement.image_titles:
                        full_path = path + image
                        titles_list = advertisement.image_titles.split(',')
                        titles_list.remove(image)
                        advertisement.image_titles = ','.join(titles_list)
                        advertisement.save()
                        try:
                            os.remove(full_path)
                        except FileNotFoundError:
                            pass

                        for size in sizes:
                            full_path = path + image[:8] + '_' + size + '.jpg'
                            try:
                                os.remove(full_path)
                            except FileNotFoundError:
                                pass
                return JsonResponse({'status': 'successful delete'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# Test method
def create_commercial(request):
    banner_url = "http://vk.com"
    adv_content = "http://127.0.0.1:8000/media/gorod-rome-italy.jpg"
    adv_title = "test adv"
    new_com = Commercial.objects.create(adv_url=banner_url, adv_content=adv_content,
                                        adv_title=adv_title, is_shown=False)
    new_com.save()
    return JsonResponse({'status': 'success'})


# Test method
def select_all(request):
    if request.method == 'GET':
        try:
            category = Category.objects.get(id=6)
            # table = category.subscribers_table

            id_list = category.select_all()

            return JsonResponse({'status': id_list})
        except ObjectDoesNotExist:
            return JsonResponse({'status': "category doesn't exist"})
    else:
        return JsonResponse({'status': 'request_error'})


def periodic_task(request):
    if request.method == 'GET':
        category_list = Category.objects.all()
        critical_count = 7   # critical count of new advs to push notification
        for category in category_list:

            if category.notification_counter >= critical_count:

                id_list = category.select_all()  # get list of all user's id from category table

                for user_id in id_list:
                    user = User.objects.get(id=user_id)
                    # get device token from User.field, devices registered on GCM
                    pass
                    # push notification method for Android
                    # push notification method for iOS

                category.notification_counter = 0
                category.save()

        return JsonResponse({'status': 'successful'})
    else:
        return JsonResponse({'status': 'request_error'})
