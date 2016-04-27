# -*- coding: utf-8 -*
import uuid
import hashlib
import time
from smtplib import SMTPException

from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render
from django.db import IntegrityError
from django.core import serializers


from .models import *
from django.contrib import auth


import datetime
import json
import sqlite3
from parsing_string import *
from file_methods import *
from notifications import gcm_notification, apns_notification
from .utils import *

def initialize(request):  # load main.html
    context = dict()
    return render(request, '', context)


# final version
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            return JsonResponse({"status": "user with such username already exist"})
        else:
            password = request.POST['password']
            new_user = User.objects.create_user(username=username, password=password, email=email)
            new_user.save()

            token = generate_token(new_user.username)
            # token equal activation_key !!!!!
            new_profile = Profile(user=new_user, token=token)   # activation_key=token

            new_profile.save()

            return JsonResponse({"status": "successful user registration", "token": token})
    else:
        return JsonResponse({"status": "error"})


# final version
def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            profile = Profile.objects.get(user=user)

            return JsonResponse({"status": "successful log in", "token": profile.token})
        else:
            return JsonResponse({"status": "authentication error"})
    else:
        return JsonResponse({"status": "error"})


# final version
def log_out(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            user_profile.token = generate_token(user_profile.user.username)
            user_profile.save()

            return JsonResponse({"status": "successful log out"})
    else:
        return JsonResponse({"status": "error"})


# final version
def change_email(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            new_email = request.POST['new_email']
            user_profile.token = generate_token(new_email)
            user_profile.save()
            user_profile.user.email = new_email
            user_profile.user.save()
            user_profile.save()
            return JsonResponse({'status': 'success', 'new_token': user_profile.token})
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def change_password(request):  # mobile client handles old password check
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            new_password = request.POST['new_password']
            user_profile.token = generate_token(new_password)
            user_profile.save()
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            return JsonResponse({'status': 'password successful changed', 'new_token': user_profile.token})
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
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


# final version
def get_favorites(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            json_dict = dict()
            favorites_list = get_int_list(user_profile.userFavorites)

            json_dict['records'] = favorites_list
            json_dict['datatime'] = user_profile.datatime_favorites
            return JsonResponse(json_dict)
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def add_favorite(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            adv_id = str(request.POST['advertisement_id'])
            if adv_id in user_profile.userFavorites:
                return JsonResponse({'status': 'advertisement_id already exist in userFavorites'})
            else:
                user_profile.userFavorites = add_to_str(user_profile.userFavorites, adv_id)  # '1,2,4' + ',' + '7'
                # or only '7' if source string is empty
                user_profile.datatime_favorites = datetime.datetime.now()
                user_profile.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def delete_favorite(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            adv_id = int(request.POST['advertisement_id'])
            int_list = get_int_list(user_profile.userFavorites)  # get int list of id advertisements
            if adv_id in int_list:
                int_list.remove(adv_id)
                user_profile.userFavorites = str_from_int_list(int_list)
                user_profile.datatime_favorites = datetime.datetime.now()
                user_profile.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': "not found advertisement or user favorites string empty"})
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


#  final version
def get_subscriptions(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            json_dict = dict()
            subscriptions_list = get_int_list(user_profile.userSubscriptions)

            json_dict['records'] = subscriptions_list
            json_dict['datatime'] = user_profile.datatime_subscriptions
            return JsonResponse(json_dict)
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def add_subscription(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            try:
                category_id = str(request.POST['category_id'])
                if category_id in user_profile.userSubscriptions:
                    return JsonResponse({'status': "category_id already exist in userSubscriptions"})
                else:
                    try:
                        category = Category.objects.get(id=category_id)

                        try:
                            profile_list = list()
                            profile_list.append(user_profile.id)
                            category.insert_row_subscriber(profile_list=profile_list)

                            user_profile.userSubscriptions = add_to_str(user_profile.userSubscriptions, category_id)
                            user_profile.datatime_subscriptions = datetime.datetime.now()
                            user_profile.save()
                            return JsonResponse({'status': 'subscription successful add'})

                        except sqlite3.DatabaseError or sqlite3.DataError:
                            return JsonResponse({'status': 'database error or data error'})

                    except ObjectDoesNotExist:
                        return JsonResponse({'status': "category doesn't exist"})

            except ValueError:
                return JsonResponse({'status': "input value error"})
        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def delete_subscription(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            try:
                category_id = int(request.POST['category_id'])
                int_list = get_int_list(user_profile.userSubscriptions)  # get int list of subscriptions (id categories)
                if category_id in int_list:
                    try:
                        category = Category.objects.get(id=category_id)
                        try:
                            profile_list = list()
                            profile_list.append(user_profile.id)
                            category.delete_row_subscriber(profile_list=profile_list)   # delete from table

                            int_list.remove(category_id)
                            user_profile.userSubscriptions = str_from_int_list(int_list)    # delete from field
                            user_profile.save()

                            return JsonResponse({'status': 'subscription successful delete'})

                        except sqlite3.DatabaseError or sqlite3.DataError:
                            return JsonResponse({'status': 'database error or data error'})

                    except ObjectDoesNotExist:
                        return JsonResponse({'status': "category doesn't exist"})
                else:
                    return JsonResponse({'status': "not found subscription or user subscribers string empty"})
            except ValueError:
                return JsonResponse({'status': "input value error"})

        else:
            return JsonResponse({'status': auth_check_response['status']})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовый вариант
def add_category(request):
    Category(name='TEST').create_table_subscribers(name='testtesttest')

    return JsonResponse({'status': 'successfully added'})


# тестовый вариант
def delete_category(request):
    Category.objects.get(name='TEST').delete()

    return JsonResponse({'status': 'successfully deleted'})


# final version
def get_categories(request):
    """
    Function return data with existing categories (id, name) in json-format
    :param request: user token
    :return: json dictionary
    """
    if request.method == 'GET':  # need change to GET
        json_dict = dict()
        category_records = Category.objects.all()

        records_list = list()
        for i in range(0, len(category_records)):
            record = {
                'id': category_records[i].pk,
                'name': category_records[i].name,
            }
            records_list.append(record)
        json_dict['records'] = records_list
        json_dict['last_change'] = DatatimeTable.objects.get(name=Category._meta.db_table).datatime
        return JsonResponse(json_dict)
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def get_cities(request):
    if request.method == 'GET':  # need change to GET
        json_dict = dict()
        city_records = City.objects.all()

        records_list = list()
        for i in range(0, len(city_records)):
            record = {
                'id': city_records[i].pk,
                'name': city_records[i].name,
            }
            records_list.append(record)
        json_dict['records'] = records_list

        json_dict['last_change'] = DatatimeTable.objects.get(name=City._meta.db_table).datatime
        return JsonResponse(json_dict)
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def get_extrafields_description(request):
    if request.method == 'GET':  # need change to GET
        json_dict = dict()
        extrafield_objects = ExtraFieldDescription.objects.all()

        records_list = list()
        for extrafield in extrafield_objects:
            element = {
                'id': extrafield.id,
                'name': extrafield.name,
                'min_int': extrafield.min_int,
                'max_int': extrafield.max_int,
                'string_set': extrafield.string_set,
                'data_type': extrafield.data_type,
                'category_id': extrafield.category_id,
                'boolean': extrafield.boolean,
            }
            records_list.append(element)
        json_dict['records'] = records_list
        json_dict['last_change'] = DatatimeTable.objects.get(name=ExtraFieldDescription._meta.db_table).datatime
        return JsonResponse(json_dict)
    else:
        return JsonResponse({'status': 'request_error'})


# TEST for unixtime, class Meta etc.
def get_unixtime(request):
    if request.method == 'GET':
        s = Advertisement.objects.get(id=32).datatime   # datetime.datetime(2016, 4, 19, 10, 17, 17, 135925,
        # tzinfo=<UTC>)
        p = Advertisement.objects.get(id=33).datatime

        boolean = False
        unixtime1 = time.mktime(s.timetuple())
        if isinstance(unixtime1, float):
            boolean = True

        unixtime2 = time.mktime(p.timetuple())

        d = datetime.datetime.now()
        unixtime_now = time.mktime(d.timetuple())

        return JsonResponse({'32': unixtime1, '33': unixtime2, 'unixtime_now': unixtime_now, 'boolean': boolean,
                             'table_name': [Category._meta.db_table, City._meta.db_table,
                                            ExtraFieldDescription._meta.db_table]})
    else:
        return JsonResponse({'status': 'request_error'})


# final version, get by unix date from POST request without auth check
def get_advs_by_datatime(request):
    """
    Function return data with existing categories (id, name) in json-format
    :param request: user token, list of ids Advertisement objects
    :return:json objects
    """
    if request.method == 'POST':
        unixtime = float(request.POST['unixtime'])
        json_dict = dict()
        records = dict()
        i = 0

        advs = Advertisement.objects.all()
        for adv in advs:
            if unixtime < time.mktime(adv.datatime.timetuple()):
                category = Category.objects.get(id=adv.category_id)
                extrafield_dict = category.select_all_extrafields(advertisement_id=adv.id)

                records[i] = {
                    'id': adv.id,
                    'profile':  adv.profile.id,
                    'category':  adv.category.name,
                    'city':  adv.city.name,
                    'title': adv.title,
                    'price': adv.price,
                    'description': adv.description,
                    'condition': str(adv.condition),
                    'phone': adv.phone,
                    'datatime': adv.datatime,
                    'extrafields': extrafield_dict
                }
                i += 1

        json_dict['records'] = records
        json_dict['request_datatime'] = datetime.datetime.now()
        # json_dict['id_not_found'] = not_found_records_list
        json_dict['records_count'] = i
        return JsonResponse(json_dict)

    else:
        return JsonResponse({'status': 'request_error'})


# final version, added unix time filtration
def base_filter(request):
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'condition', 'price']
        str_filters = ['title__contains']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))
            json_dict = dict()
            records = dict()
            i = 0

            advs = Advertisement.objects.filter(**params)
            result_advs = list()    # put advs after data time filtration

            if request.POST['unixtime'] != '':
                unixtime = request.POST['unixtime']
                if isinstance(float(unixtime), float):
                    unixtime = float(request.POST['unixtime'])
                    for adv in advs:
                        if unixtime < time.mktime(adv.datatime.timetuple()):
                            result_advs.append(adv)
                else:
                    result_advs.extend(advs)
            else:
                result_advs.extend(advs)

            for adv in result_advs:
                category = Category.objects.get(id=adv.category_id)
                extrafield_dict = category.select_all_extrafields(advertisement_id=adv.id)

                records[i] = {
                    'id': adv.id,
                    'profile':  adv.profile.id,
                    'category':  adv.category.id,
                    'city':  adv.city.id,
                    'title': adv.title,
                    'price': adv.price,
                    'description': adv.description,
                    'condition': str(adv.condition),
                    'phone': adv.phone,
                    'datatime': adv.datatime,
                    'extrafields': extrafield_dict
                }
                i += 1
            json_dict['records'] = records
            json_dict['records_count'] = i

            json_dict['status'] = 'success'

            return JsonResponse(json_dict)

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def extended_filter(request):   # extend base filter
    if request.method == 'POST':
        params = dict()
        int_filters = ['category', 'city', 'condition', 'price']
        str_filters = ['title__contains']

        try:
            params.update(get_int_params(request, int_filters))
            params.update(get_str_params(request, str_filters))
            json_dict = dict()
            records = dict()
            i = 0

            advs = Advertisement.objects.filter(**params)
            filtered_advs = list()    # put advs after data time filtration

            if request.POST['unixtime'] != '':
                unixtime = request.POST['unixtime']
                if isinstance(float(unixtime), float):
                    unixtime = float(request.POST['unixtime'])

                    for adv in advs:
                        if unixtime < time.mktime(adv.datatime.timetuple()):
                            filtered_advs.append(adv)
                else:
                    filtered_advs.extend(advs)  # get filtered objects by unixtime
            else:
                filtered_advs.extend(advs)  # get filtered objects by params

            result_advs = list()  # advs after extra fields filtration or not
            if request.POST['json_object'] != '':  # check for extra fields params
                data = json.loads(request.POST.get('json_object'))
                list_of_dictionary = data['extrafields']
                for adv in filtered_advs:
                    counter = 0
                    for dictionary in list_of_dictionary:
                        if adv.category.select_row_extrafield(extrafield_id=int(dictionary['id']),
                                                              advertisement_id=adv.id,
                                                              string_value=dictionary['value']):
                            # search extra field from POST to current adv
                            counter += 1
                    if counter == len(list_of_dictionary):  # if find all extra fields from POST to current adv
                        result_advs.append(adv)
            else:
                result_advs.extend(filtered_advs)

            for adv in result_advs:  # formation adv to json response
                extrafield_dict = adv.category.select_all_extrafields(advertisement_id=adv.id)

                records[i] = {
                    'id': adv.id,
                    'profile':  adv.profile.id,
                    'category':  adv.category.id,
                    'city':  adv.city.id,
                    'title': adv.title,
                    'price': adv.price,
                    'description': adv.description,
                    'condition': str(adv.condition),
                    'phone': adv.phone,
                    'datatime': adv.datatime,
                    'extrafields': extrafield_dict
                }
                i += 1
            json_dict['records'] = records
            json_dict['records_count'] = i

            json_dict['status'] = 'success'

            return JsonResponse(json_dict)

        except ValueError:
            return JsonResponse({'status': 'value_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# final version, data = json.loads(request.POST.get('json_object'))
def add_adv(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            params = dict()
            int_args = ['condition', 'price']
            str_args = ['title', 'description', 'phone']

            for key in str_args:
                if request.POST[key] == '':
                    return JsonResponse({'status': 'parameters_error'})

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

                advertisement = Advertisement.objects.create(**params)  # must be IntegrityError or ObjectDoesNotExist

                if advertisement:
                    advertisement.save()
                    advertisement.category.notification_counter += 1
                    advertisement.category.save()

                    data = json.loads(request.POST.get('json_object'))
                    list_of_dictionary = data['extrafields']
                    for dictionary in list_of_dictionary:
                        advertisement.category.insert_row_extrafield(extrafield_id=dictionary['id'],
                                                                     advertisement_id=advertisement.id,
                                                                     string_value=str(dictionary['value']))

                    return JsonResponse({'status': 'Advertisement successful add'})

            except IntegrityError or ObjectDoesNotExist:
                return JsonResponse({'status': 'parameters_error'})

        else:
            return JsonResponse({'status': 'authentication_error or missing token'})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def del_adv(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
            adv_id = request.POST['adv_id']
            try:
                adv = Advertisement.objects.get(pk=adv_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'advertisement not found'})
            except ValueError:
                return JsonResponse({'status': "adv_id value error"})
            else:
                if adv.profile.pk == user_profile.pk:
                    category = Category.objects.get(id=adv.category_id)  # get related category object
                    category.delete_rows_extrafield(advertisement_id=adv.id)  # delete extra fields related with adv

                    if adv.image_titles != '':
                        sizes = ('L', 'M', 'S')
                        image_list = adv.image_titles.split(',')
                        path = user_profile.folder_path

                        for image in image_list:
                            full_path = path + image
                            try:
                                os.remove(full_path)    # delete source image
                            except FileNotFoundError or IsADirectoryError:
                                pass

                            for size in sizes:  # delete different sizes images
                                full_path = path + image[:8] + '_' + size + '.jpg'
                                try:
                                    os.remove(full_path)
                                except FileNotFoundError or IsADirectoryError:
                                    pass

                        adv.delete()
                        return JsonResponse({'status': 'success'})
                    else:
                        adv.delete()
                        return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def edit_adv(request):
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
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

                    data = json.loads(request.POST.get('json_object'))  # change extra fields in adv
                    list_of_dictionary = data['extrafields']
                    try:
                        for dictionary in list_of_dictionary:
                            adv.category.update_row_extrafield(string_value=str(dictionary['value']),
                                                               extrafield_id=int(dictionary['id']),
                                                               advertisement_id=int(adv.id))
                    except sqlite3.DatabaseError or sqlite3.DataError:
                        return JsonResponse({'status': 'database error or data error'})

                    return JsonResponse({'status': 'success'})

                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# final version
def upload_photos(request):
    """
    Function processes the incoming images
    :param request: user token, advertisement id
    :return: status, list of failed upload files || (&&) list of success upload files
    """
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
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


# final version
def delete_photos(request):  # final version
    """
    Function processes the incoming requests to delete photos
    :param request: user token, advertisement id, string of images names
    :return: json response
    """
    if request.method == 'POST':
        auth_check_response = auth_check(request)
        if auth_check_response['code'] == 0:
            user_profile = auth_check_response['profile']
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


#  not final version / Test method
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
            category = Category.objects.get(id=26)
            # table = category.subscribers_table

            id_list = category.select_all_subscribers()

            return JsonResponse({'status': id_list})
        except ObjectDoesNotExist:
            return JsonResponse({'status': "category doesn't exist"})
    else:
        return JsonResponse({'status': 'request_error'})


# not final version / Test method
def periodic_task(request):  # test version
    if request.method == 'GET':
        category_list = Category.objects.all()
        critical_count = 7   # critical count of new advs to push notification. unreaded notifications number
        log_dict = dict()   # different instance of communication with GCM

        for category in category_list:

            if category.notification_counter >= critical_count:

                id_list = category.select_all_subscribers()  # get list of all user's id from category table
                title = 'Bazzzar notification'
                message = 'Appears {0} advs in category {1}'.format(category.notification_counter,
                                                                    category.name)
                android_tokens = list()
                ios_tokens = list()

                for user in id_list:
                    try:
                        profile = Profile.objects.get(user_id=user)

                        # get device token from Profile.field, devices registered on GCM
                        android_tokens.extend(profile.android_tokens.split(','))

                        # get device token from Profile.field, devices registered on APNs
                        ios_tokens.extend(profile.ios_tokens.split(','))

                    except ObjectDoesNotExist:
                        pass

                # push notification method for Android
                log_dict[category.name] = gcm_notification(android_tokens, title, message)

                # push notification method for iOS
                """
                apns_notification(ios_tokens, message)            # <<<<<<-------------------- iOS  notification
                """

                category.notification_counter = 0
                category.save()

        return JsonResponse({'status': 'successful send notifications', 'logo': log_dict})
    else:
        return JsonResponse({'status': 'request_error'})


# Test stuff
def ping(request):
    set = Category.objects.all()
    data = serializers.serialize('xml', set, fields=('pk', 'name', 'notification_counter'), ensure_ascii=False)
    return HttpResponse(data, content_type='application/json; charset=utf8', status=200)