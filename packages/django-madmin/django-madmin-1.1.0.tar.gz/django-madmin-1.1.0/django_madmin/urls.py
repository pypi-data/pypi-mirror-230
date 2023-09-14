from django.urls import path
from django.urls import reverse
from . import views


def reverse_check_upload_url():
    return reverse(views.check_upload)


madmin_urls = [
    path('madmin/upload/', views.upload, name="upload"),
    path('madmin/check_upload/', views.check_upload, name="check_upload"),
]
