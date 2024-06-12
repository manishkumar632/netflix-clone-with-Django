from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("signup", views.signup, name="signup"),
    path("movie/<str:pk>", views.movie, name="movie"),
    path("my-list", views.my_list, name="my_list"),
    path("home-add-to-list", views.home_add_to_list, name="home-add-to-list"),
    path("search-add-to-list", views.search_add_to_list, name="search-add-to-list"),
    path("search", views.search, name="search"),
    path("trailer", views.trailer, name="trailer"),
    path("genre/<str:genre>", views.genre, name="genre"),
    path("remove-from-list", views.remove_from_list, name="remove-movie-from-list"),
]
