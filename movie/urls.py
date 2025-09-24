from django.urls import path
from .views import recommend_view

app_name = "movie"
urlpatterns = [
    path("recommend/", recommend_view, name="recommend"),
]