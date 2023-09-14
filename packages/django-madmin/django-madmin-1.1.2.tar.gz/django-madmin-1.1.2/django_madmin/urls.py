from django.urls import path
from . import views


madmin_urls = [
    path('madmin/upload/', views.upload, name="upload"),
    path('madmin/check_upload/', views.check_upload, name="check_upload"),
]
