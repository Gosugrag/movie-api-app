from django.db import models
from django.conf import settings


class StreamingPlatform(models.Model):
    name = models.CharField(max_length=30)
    about = models.TextField()
    website = models.URLField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class WatchList(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    streaming_platforms = models.ManyToManyField(StreamingPlatform)

    def __str__(self):
        return self.title
