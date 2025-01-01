"""
URL mapping for the watchlist app.
"""
from django.urls import path

from watchlist import views

app_name = 'watchlist'

urlpatterns = [
    path('watchlist/', views.WatchListView.as_view(), name='watchlist-list'),
    path('watchlist/<int:pk>/', views.WatchListDetailView.as_view(),
         name='watchlist-detail'),
    path('streaming-platforms/', views.StreamingPlatformListView.as_view(), name='streamingplatform-list'),
    path('streaming-platforms/<int:pk>/', views.StreamingPlatformDetailView.as_view(), name='streamingplatform-detail'),
]
