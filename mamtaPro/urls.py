"""mamtaPro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include("mamtaApp.urls", namespace='mamtaApp')),
    url(r'^invoice/', include("invoice.urls", namespace='invoiceApp')),
    url(r'^attendance/', include("attendance.urls", namespace='attendanceApp')),
    url(r'^api/', include('mamtaApp.api.urls')),
    url(r'^invoiceApi/', include('invoice.api.urls')),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url('', include('pwa.urls')),
]
handler404 = 'mamtaApp.views.bad_request'
handler500 = 'mamtaApp.views.bad_server'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)