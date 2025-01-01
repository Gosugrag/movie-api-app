# from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.models import WatchList, StreamingPlatform
from watchlist.serializers import (WatchListSerializer,
                                   StreamingPlatformSerializer)


class WatchListView(APIView):
    """API view for listing Movie object"""
    serializer_class = WatchListSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return WatchList.objects.all().order_by('title')

    def get_permissions(self):
        permissions = {
            'POST': [IsAuthenticated()],
            'GET': [AllowAny()],
        }
        return permissions.get(self.request.method, [AllowAny()])

    def get(self, request, format=None):
        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WatchListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchListDetailView(APIView):
    """API view for retrieving, changing and deleting Movie object"""
    serializer_class = WatchListSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        permissions = {
            'POST': [IsAuthenticated()],
            'PUT': [IsAuthenticated()],
            'DELETE': [IsAuthenticated()],
            'GET': [AllowAny()],
        }
        return permissions.get(self.request.method, [AllowAny()])

    def get(self, request, pk, format=None):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"error": "Movie not found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"error": "Movie not found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk,  format=None):
        try:
            movie = WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({"error": "Movie not found"},
                            status=status.HTTP_404_NOT_FOUND)
        movie.delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StreamingPlatformListView(APIView):
    """API view for retrieving and creating StreamingPlarformView object by id"""
    serializer_class = StreamingPlatformSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        permissions = {
            'POST': [IsAuthenticated()],
            'GET': [AllowAny()],
        }
        return permissions.get(self.request.method, [AllowAny()])

    def get(self, request, format=None):
        streaming_platform_list = StreamingPlatform.objects.all().order_by('title')
        serializer = self.serializer_class(streaming_platform_list, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamingPlatformDetailView(APIView):
    """API view for retrieving, changing and deleting StreamingPlatformView object"""
    serializer_class = StreamingPlatformSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        permissions = {
            'POST': [IsAuthenticated()],
            'PUT': [IsAuthenticated()],
            'DELETE': [IsAuthenticated()],
            'GET': [AllowAny()],
        }
        return permissions.get(self.request.method, [AllowAny()])

    def get(self, request, pk, format=None):
        try:
            platform = StreamingPlatform.objects.get(pk=pk)
        except StreamingPlatform.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(platform)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        try:
            platform = StreamingPlatform.objects.get(pk=pk)
        except StreamingPlatform.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(platform, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            platform = StreamingPlatform.objects.get(pk=pk)
        except StreamingPlatform.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
        platform.delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# @extend_schema(
#     request=MovieSerializer,  # Request schema for POST
#     responses={
#         200: MovieSerializer(many=True),  # Response schema for GET
#         201: MovieSerializer,  # Response schema for successful POST
#         400: {
#             "type": "object",
#             "properties": {
#                 "error": {"type": "string", "example":
#                           "Invalid query parameter provided."},
#             },
#         },
#     },
#     description="List all movies (GET) or create a new movie (POST).",
# )
# @api_view(['GET', 'POST'])
# def movie_list(request):
#     """List movies or create a new movie"""
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,
#         status=status.HTTP_400_BAD_REQUEST)
#
#
# @extend_schema(
#     request=MovieSerializer,  # Request schema for PUT
#     responses={
#         200: MovieSerializer,  # Response schema for GET and PUT
#         204: None,  # Response schema for DELETE
#         400: {
#             "type": "object",
#             "properties": {
#                 "error": {"type": "string", "example":
#                           "Validation error details"},
#             },
#         },
#         404: {
#             "type": "object",
#             "properties": {
#                 "error": {"type": "string", "example": "Movie not found"},
#             },
#         },
#     },
#     description="Retrieve, update, or delete a specific movie.",
# )
# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_detail(request, pk):
#     """Retrieve, update, or delete a specific movie"""
#     try:
#         movie = Movie.objects.get(pk=pk)
#     except Movie.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = MovieSerializer(movie, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors,
#         status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
