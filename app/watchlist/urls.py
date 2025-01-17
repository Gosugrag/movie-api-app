"""
URL mapping for the watchlist app.
"""
from django.urls import path, include

from watchlist import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('streaming', views.StreamingPlatformViewSet,
                basename='streaming')

app_name = 'watch'

urlpatterns = [
    path('watch/', views.WatchListView.as_view(), name='watchlist-list'),
    path('watch/<int:pk>/', views.WatchListDetailView.as_view(),
         name='watchlist-detail'),
    path('', include(router.urls)),
    # path('streaming/', views.StreamingPlatformListView.as_view(),
    # name='streamingplatform-list'),
    # path('streaming/<int:pk>/', views.StreamingPlatformDetailView.as_view(),
    # name='streamingplatform-detail'),
    path('watch/<int:pk>/reviews/', views.ReviewListView.as_view(),
         name='reviews-list'),
    path('watch/<int:watch_pk>/reviews/<int:review_pk>/',
         views.ReviewDetailView.as_view(), name='reviews-detail'),
    path('watch/reviews/user/<int:pk>', views.UserReviewListView.as_view(),
         name='reviews-user'),
]
