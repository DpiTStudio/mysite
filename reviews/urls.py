from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.reviews_list, name="list"),
    path("create/", views.create_review, name="create"),
]
