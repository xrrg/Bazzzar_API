import hashlib

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import *


# final version
def auth_check(request):
    """
    Correct input and permissions check. Returns user profile and code '0' in case of success
    as dictionary and returns code '1' in case of failing, and code '2' in case of
    wrong token.
    """
    auth_check_report = dict()
    auth_check_report['profile'] = None
    try:
        request_token = request.POST['token']
        username = request.POST['username']
    except Exception:
        auth_check_report['status'] = 'params_error'
        auth_check_report['code'] = 1
        return auth_check_report
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        auth_check_report['status'] = 'user_not_found'
        auth_check_report['code'] = 1
        return auth_check_report
    else:
        if user and request_token != '':
            try:
                user_profile = Profile.objects.get(user=user)
            except ObjectDoesNotExist:
                auth_check_report['status'] = 'profile_not_found'
                auth_check_report['code'] = 1
            else:
                if user_profile.token == request_token:
                    auth_check_report['status'] = 'success'
                    auth_check_report['code'] = 0
                    auth_check_report['profile'] = user_profile
                else:
                    auth_check_report['status'] = 'wrong_token'
                    auth_check_report['code'] = 2
            finally:
                return auth_check_report


def generate_token(input_string=str()):
    salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    salted_username = salt + input_string
    token = hashlib.sha1(salted_username.encode('utf-8')).hexdigest()
    return token


# final version
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


# final version
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


# final version
def set_token(request):
    """
    Function set device's tokens to user profile
    :param request: User token, tokens_list
    :return: json response
    """
    if request.method == 'POST':
        user_profile = auth_check(request)
        if user_profile != 1:
            # keys = list(request.POST.keys())
            if request.POST['android'] != '':
                if user_profile.android_tokens != '':
                    tokens_list = user_profile.android_tokens.split(',')

                    if request.POST['android'] in tokens_list:
                        return JsonResponse({'status': "token exist"})
                    else:
                        tokens_list.append(request.POST['android'])
                        user_profile.android_tokens = ','.join(tokens_list)
                else:
                    user_profile.android_tokens = request.POST['android']
                user_profile.save()
                return JsonResponse({'status': 'successful add android token'})

            elif request.POST['ios'] != '':
                if user_profile.ios_tokens != '':
                    tokens_list = user_profile.ios_tokens.split(',')

                    if request.POST['ios'] in tokens_list:
                        return JsonResponse({'status': "token exist"})
                    else:
                        tokens_list.append(request.POST['ios'])
                        user_profile.ios_tokens = ','.join(tokens_list)
                else:
                    user_profile.ios_tokens = request.POST['ios']
                user_profile.save()
                return JsonResponse({'status': 'successful add ios token'})

            else:
                return JsonResponse({'status': "request didn't have the necessary data"})
        else:
            return JsonResponse({'status': 'authentication_error'})
    else:
        return JsonResponse({'status': 'request_error'})