from django.db import models
from django.conf import settings

# Create your models here.
class Movie(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE)

    def __str__(self):
        return self.name
