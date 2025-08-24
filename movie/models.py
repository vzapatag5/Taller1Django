from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='movies/images/')  # ✅ SIN "media/"
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)

    def _str_(self):
        return self.title
    