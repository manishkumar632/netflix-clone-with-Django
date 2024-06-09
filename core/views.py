from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from datetime import datetime
from django.contrib.auth.decorators import login_required
import re, requests, json, urllib.parse
from django.http import JsonResponse
from django.core.serializers import serialize
from decouple import config
from datetime import datetime


@login_required(login_url="login")
def convetDateTime(date):
    date_str = date
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%b %d, %Y")
    print(formatted_date)
    return formatted_date


def index(request):
    movies = Movie.objects.exclude(image_card__isnull=True).exclude(
        image_card__exact=""
    )
    return render(request, "index.html", {"movies": movies})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("login")
    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect("signup")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email
                )
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect("/")
        else:
            messages.info(request, "Password not matching")
            return redirect("signup")

    return render(request, "signup.html")


@login_required(login_url="login")
def movie(request, pk):
    movie = Movie.objects.get(uu_id=pk)
    context = {"movie_details": movie}
    return render(request, "movie.html", {"movie": movie})


@login_required(login_url="login")
def my_list(request):
    return render(request, "my_list.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    return redirect("/")


@login_required(login_url="login")
def add_to_list(request):
    if request.method == "POST":
        tmdb_id = request.POST["tmdb_id"]
        movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
        movie_in_list, created = MovieList.objects.get_or_create(
            owner_user=request.user, movie=movie
        )
        if created:
            response_data = {"status": "success", "message": "Added ✔"}
        else:
            response_data = {"status": "error", "message": "Movie already in your list"}

        return JsonResponse(response_data)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})


@login_required(login_url="login")
def my_list(request):
    movie_lists = MovieList.objects.filter(owner_user=request.user)
    movie_list = [movie.movie for movie in movie_lists]
    movie_list_json = serialize(
        "json",
        movie_list,
        fields=(
            "title",
            "description",
            "release_date",
            "get_genre_display",
            "length",
            "image_card",
            "image_cover",
            "uu_id",
        ),
    )
    return render(request, "my_list.html", {"movies_json": movie_list_json})


def search(request):
    if request.method == "POST":
        search_term = request.POST.get("search_term", "")
        encoded_search_term = urllib.parse.quote_plus(search_term)
        url = f"https://api.themoviedb.org/3/search/movie?query={encoded_search_term}"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + config("TOKEN"),
        }
        response = requests.get(url, headers=headers)
        movies_data = response.json().get("results", [])
        return render(
            request, "search.html", {"search_term": search_term, "movies": movies_data}
        )
    return render(request, "search.html", {"search_term": "", "movies": []})
