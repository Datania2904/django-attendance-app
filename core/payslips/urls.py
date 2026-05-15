from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_payslips, name="upload_payslips"),
    path("my/", views.my_payslips, name="my_payslips"),
]
