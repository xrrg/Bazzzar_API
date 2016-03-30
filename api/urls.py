from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'register/', views.register),
    url(r'login/', views.log_in),
    url(r'logout/', views.log_out),
    url(r'change_email/', views.change_email),
    url(r'change_password/', views.change_password),

    # url(r'about/', views.documentation),
    url(r'add/', views.add_category),   # test function
    url(r'insert_row/', views.insert_row),  # test function
    url(r'delete_row/', views.delete_row),  # test function
    url(r'delete/', views.delete_category),  # test function

    url(r'add_favorite/', views.add_favorite),
    url(r'del_favorite/', views.delete_favorite),
    url(r'subscribe/', views.add_subscription),
    url(r'del_subscription/', views.delete_subscription),

    url(r'get_categories/', views.get_categories),
    url(r'get_advs_by_id/', views.get_advs_by_id),
    url(r'add_adv/', views.add_adv),

    url(r'base_filter/', views.base_filter),
    url(r'house_filter/', views.house_filter),
    url(r'transport_filter/', views.transport_filter),
    url(r'clothes_filter/', views.clothes_filter),
    url(r'kidsthings_filter/', views.kidsthings_filter),
    url(r'tourism_filter/', views.tourism_filter),

    url(r'', views.initialize),
]
