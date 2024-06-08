from django.contrib import admin
from .models import Movie, MovieList

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_date', 'length', 'movie_views', 'image_cover', 'image_card', 'video', 'uu_id')

class MovieListAdmin(admin.ModelAdmin):
    list_display = ('owner_user', 'movie')


admin.site.register(MovieList, MovieListAdmin)
admin.site.register(Movie, MovieAdmin)
