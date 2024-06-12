from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from django.contrib.auth.decorators import login_required
import requests, json, urllib.parse
from django.http import JsonResponse
from decouple import config

accept = config("ACCEPT", )
authorization = config("AUTHORIZATION")
headers = {
    "accept": accept,
    "Authorization": authorization,
}
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
    return render(request, "movie.html", {"movie": movie})


@login_required(login_url="login")
def my_list(request):
    return render(request, "my_list.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    return redirect("/")


@login_required(login_url="login")
def home_add_to_list(request):
    if request.method == "POST":
        movie = Movie.objects.get(tmdb_id=request.POST["tmdb_id"])
        if MovieList.objects.filter(owner_user=request.user, movie=movie).exists():
            return JsonResponse(
                {"status": "error", "message": "Movie already in your list"}
            )
        else:
            MovieList.objects.create(owner_user=request.user, movie=movie)
            return JsonResponse({"status": "success", "message": "Added ✔"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})


@login_required(login_url="login")
def my_list(request):
    movie_lists = MovieList.objects.filter(owner_user=request.user)
    movie_list = [movie.movie for movie in movie_lists]
    return render(request, "my_list.html", {"movies": movie_list})


def search(request):
    if request.method == "POST":
        search_term = request.POST.get("search_term", "")
        encoded_search_term = urllib.parse.quote_plus(search_term)
        url = f"https://api.themoviedb.org/3/search/movie?query={encoded_search_term}"
        response = requests.get(url, headers=headers)
        movies_data = response.json().get("results", [])
        movies_data = [movie for movie in movies_data if movie.get("backdrop_path")]
        movie_ids = [movie["id"] for movie in movies_data]

        for id in movie_ids:
            url = "https://api.themoviedb.org/3/movie/{}".format(id)
            response = requests.get(url, headers=headers)
            movie = response.json()
            movies_data[movie_ids.index(id)] = movie
        return render(
            request, "search.html", {"search_term": search_term, "movies": movies_data}
        )
    return render(request, "search.html", {"search_term": "", "movies": []})


@login_required(login_url="login")
def search_add_to_list(request):
    if request.method == "POST":
        movie_data = request.POST.get("movie")
        movie_data = json.loads(movie_data)
        id = movie_data.get("id")
        if MovieList.objects.filter(owner_user=request.user, movie__tmdb_id=id).exists():
            return JsonResponse(
                {"status": "error", "message": "Movie already in your list"}
            )
        movie, created = Movie.objects.get_or_create(tmdb_id=id, defaults=movie_data)
        MovieList.objects.create(owner_user=request.user, movie=movie)
        return JsonResponse({"status": "success", "message": "Added ✔"})

def trailer(request):
    id = request.GET.get("id")
    url = "https://api.themoviedb.org/3/movie/{}/videos".format(id)
    response = requests.get(url, headers=headers)
    data = response.json()
    filtered_data = [video for video in data["results"] if video["type"] == "Trailer"]
    if not filtered_data:
        return render(request, "movie.html")
    else:
        return render(request, "movie.html", {"key": filtered_data[0]["key"]})


def genre(request, genre):
    movies = Movie.objects.filter(genre__icontains=genre)
    return render(request, "genre.html", {"movies": movies})


def remove_from_list(request):
    if request.method == "POST":
        movie_id = request.POST.get("id")
        MovieList.objects.filter(owner_user=request.user, movie__tmdb_id=movie_id).delete()
        return JsonResponse({"status": "success", "message": "Removed ✔"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})
