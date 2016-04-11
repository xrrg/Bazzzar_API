"""bazzzar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
from django.conf.urls.static import static
from bazzzar.settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace="api")),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)

# http://127.0.0.1:8000/media/00/00/00/00/03/kosmos-planety-zvezdy-5340.jpg
# http://127.0.0.1:8000/media/00/00/00/00/03/skgafoss-waterfall-skg.jpg
