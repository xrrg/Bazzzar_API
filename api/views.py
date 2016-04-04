# -*- coding: utf-8 -*
import os
import hashlib
# from datetime import date
# import random

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
# from django.contrib.auth.models import User
# from django.utils import timezone

from .models import *
from django.contrib import auth

# import json
import sqlite3
from parsing_string import *


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
        # userFavorites_table = UserFavorites()
        # userFavorites_table.save()
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


# тестовая дичь! будь осторожен, путник
def insert_row(request):
    profile_list = list()
    user = User.objects.get(id=3)   # can delete list of records

    # for user in users:
    profile_list.append(user.id)    # добавление записи в список, для последующей передачи

    category = Category.objects.get(name='LOL')
    category.insert_row(table_name=category.subscribers_table,
                        profile_list=profile_list)

    return JsonResponse({'status': 'successfully add row'})


def add_subscription(request):  # TODO: db structure will be changed
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            category_id = request.POST['category_id']
            category = Category.objects.get(id=category_id)

            if category:
                try:
                    profile_list = list()
                    profile_list.append(user_profile.id)
                    category.insert_row(table_name=category.subscribers_table,
                                        profile_list=profile_list)
                    return JsonResponse({'status': 'subscription successful add'})

                except sqlite3.DatabaseError or sqlite3.DataError:
                    return JsonResponse({'status': 'database error or data error'})
            else:
                return JsonResponse({'status': "category doesn't exist "})

        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовая дичь! будь осторожен, путник
def delete_row(request):
    profile_list = list()
    user = User.objects.get(id=3)   # can delete list of users

    # for user in users:
    profile_list.append(user.id)    # добавление записи в список, для последующей передачи

    category = Category.objects.get(name='LOL')
    category.delete_row(table_name=category.subscribers_table,
                        profile_list=profile_list)

    return JsonResponse({'status': 'successfully delete row'})


def delete_subscription(request):  # TODO: db structure will be changed
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            category_id = request.POST['category_id']
            category = Category.objects.get(id=category_id)

            if category:
                try:
                    profile_list = list()
                    profile_list.append(user_profile.id)
                    category.delete_row(table_name=category.subscribers_table,
                                        profile_list=profile_list)
                    return JsonResponse({'status': 'subscription successful delete'})

                except sqlite3.DatabaseError or sqlite3.DataError:
                    return JsonResponse({'status': 'database error or data error'})
            else:
                return JsonResponse({'status': "category doesn't exist "})

        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


# тестовая дичь! будь осторожен, путник
def add_category(request):
    Category(name='#').save()

    return JsonResponse({'status': 'successfully added'})


# тестовая дичь! будь осторожен, путник
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
    if request.method == 'POST':  # POST is just for testing. TODO:change to DELETE
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
                kwargs[name] = request.POST[name]

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
    if request.method == 'POST':  # POST is just for testing. TODO:change to DELETE
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
                    return JsonResponse({'status': 'Advertisement successful add'})

            except Exception:
                return JsonResponse({'status': 'parameters_error'})

        else:
            return JsonResponse({'status': 'authentication_error or missing token'})
    else:
        return JsonResponse({'status': 'request_error'})


###############################################################################################
def del_adv(request):
    if request.method == 'POST':  # POST is just for testing. TODO:change to DELETE
        user_profile = auth_check(request)
        if user_profile != 1:
            adv_id = request.POST['adv_id']
            try:
                adv = Advertisement.objects.get(pk=adv_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'advertisement not found'})
            else:
                if adv.profile.pk == user_profile.pk:
                    adv.delete()
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def edit_adv(request):
    if request.method == 'POST':  # POST is just for testing. TODO:change to DELETE
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
                    # category_id = payload['category_id']
                    city_id = payload['city_id']
                    for arg in arg_set:
                        if arg in payload:
                            setattr(adv, arg, payload[arg])
                        else:
                            continue
                    # if category_id != '':
                    #     adv.category = Category.objects.get(pk=category_id)
                    if city_id != '':
                        adv.city = City.objects.get(pk=city_id)
                    adv.save()
                    return JsonResponse({'status': 'success'})

                else:
                    return JsonResponse({'status': 'permission_error'})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})


def upload_photos(request):
    if request.method == 'POST':  # POST is just for testing. TODO:change to DELETE
        user_profile = auth_check(request)
        if user_profile != 1:
            pass
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})