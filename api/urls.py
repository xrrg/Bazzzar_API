from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'register/', views.register),
    url(r'login/', views.log_in),
    url(r'logout/', views.log_out),
    url(r'change_email/', views.change_email),
    url(r'change_password/', views.change_password),
    url(r'reset_password/', views.reset_password),

    # url(r'about/', views.documentation),
    url(r'add/', views.add_category),   # test function
    url(r'delete/', views.delete_category),  # test function
    url(r'get_unixtime/', views.get_unixtime),  # test function

    url(r'add_favorite/', views.add_favorite),
    url(r'del_favorite/', views.delete_favorite),
    url(r'subscribe/', views.add_subscription),
    url(r'del_subscription/', views.delete_subscription),

    url(r'get_categories/', views.get_categories),
    url(r'get_advs_by_datatime/', views.get_advs_by_datatime),
    url(r'get_cities/', views.get_cities),
    url(r'get_favorites/', views.get_favorites),
    url(r'get_subscriptions/', views.get_subscriptions),
    url(r'get_extrafields_description/', views.get_extrafields_description),
    url(r'add_adv/', views.add_adv),
    url(r'edit_adv/', views.edit_adv),
    url(r'del_adv/', views.del_adv),

    url(r'ping/', views.ping),

    url(r'base_filter/', views.base_filter),
    url(r'extended_filter/', views.extended_filter),
    # url(r'house_filter/', views.house_filter),
    # url(r'transport_filter/', views.transport_filter),
    # url(r'clothes_filter/', views.clothes_filter),
    # url(r'kidsthings_filter/', views.kidsthings_filter),
    # url(r'tourism_filter/', views.tourism_filter),
    url(r'upload_photos/', views.upload_photos),
    url(r'delete_photos/', views.delete_photos),
    url(r'create_commercial/', views.create_commercial),  # test
    url(r'select_all/', views.select_all),  # test
    url(r'set_token/', views.set_token),
    url(r'periodic_task/', views.periodic_task),

    url(r'', views.initialize),
]
