"""
URL mapping for the movie app.
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from movie import views

app_name = 'movie'

urlpatterns = [
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
]
