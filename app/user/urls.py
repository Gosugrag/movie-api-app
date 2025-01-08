"""
URL mappings for the user API
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.ObtainExpiringAuthToken.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('log-out/', views.LogOutView.as_view(), name='log-out'),
    path('jwt-token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt-token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
