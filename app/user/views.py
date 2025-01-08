"""
Views for the user API
"""
import datetime

from django.contrib.auth import logout
from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class LogOutView(generics.GenericAPIView):
    """Delete token on log out"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            # Attempt to delete the token associated with the logged-in user
            request.user.auth_token.delete()
            logout(request)
            return Response(status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            # In case the user doesn't have a token
            return Response({'detail': 'Token does not exist or already deleted.'},
                            status=status.HTTP_400_BAD_REQUEST)

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class ObtainExpiringAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created =  Token.objects.get_or_create(user=serializer.validated_data['user'])

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow()
                token.save()

            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve the authenticated user"""
        return self.request.user
