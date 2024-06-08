from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class Movie(models.Model):
    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
        ('Romance', 'Romance'),
        ('Thriller', 'Thriller'),
        ('Science Fiction', 'Science Fiction'),
        ('Fantasy', 'Fantasy'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=255, choices=GENRE_CHOICES)
    length = models.PositiveIntegerField()
    image_card = models.FileField(upload_to='image_card/', blank=True, null=True)
    image_cover = models.FileField(upload_to='images_cover/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    movie_views = models.IntegerField(default=0)
    uu_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.title


class MovieList(models.Model):
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)