from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


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
    description = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    average_rating = models.FloatField(validators=[MinValueValidator(0)],
                                       default=None,
                                       null=True)
    total_reviews = models.PositiveIntegerField(default=0)
    platform = models.ForeignKey(StreamingPlatform,
                                 on_delete=models.CASCADE,
                                 related_name='watchlist',
                                 default=None,
                                 null=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    watchlist = models.ForeignKey(WatchList,
                                  on_delete=models.CASCADE,
                                  related_name='reviews',
                                  default=None)
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.rating) + ' | ' + self.watchlist.title
