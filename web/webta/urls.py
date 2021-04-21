from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_scanner', views.add_scanner, name='add_scanner'),
    path('add_api', views.add_api, name='add_api'),
    path('scanner/<int:scanner_serial>', views.open_scan, name='open_scan'),
]