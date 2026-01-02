from django.urls import path
from . import views

app_name = "mail"

urlpatterns = [
    path("", views.mail_index, name="index"),
    path("send-test/", views.send_test_email, name="send_test"),
]
