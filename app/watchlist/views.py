# from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from django.db.models import Avg, Count
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from rest_framework import status, viewsets
from core.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from rest_framework import mixins
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from core.pagination import WatchListPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import (BasicAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        IsAuthenticatedOrReadOnly,
                                        IsAdminUser)
from core.models import WatchList, StreamingPlatform, Review
from watchlist.serializers import (WatchListSerializer,
                                   StreamingPlatformSerializer,
                                   ReviewSerializer)


class UserReviewListView(mixins.ListModelMixin,
                         generics.GenericAPIView):
    """API view for listing Reviews for a specific user."""
    serializer_class = ReviewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly | IsAdminUser,)

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        if not user_id:
            raise PermissionDenied("User ID is required.")

        return Review.objects.filter(user_id=user_id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ReviewListView(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    """API view for listing Review object"""
    serializer_class = ReviewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly|IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user',)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Review.objects.filter(watchlist=pk).order_by('-created_at')

    # def get_permissions(self):
    #     permissions = {
    #         'POST': [IsAuthenticated()],
    #         'GET': [AllowAny()],
    #     }
    #     return permissions.get(self.request.method, [AllowAny()])

    def perform_create(self, serializer):
        watchlist_pk = self.kwargs.get('pk')
        watchlist = get_object_or_404(WatchList, pk=watchlist_pk)

        review_user = self.request.user
        review_queryset_exist = Review.objects.filter(watchlist=watchlist, user=review_user).exists()

        if review_queryset_exist:
            raise ValidationError('Review already exists')

        serializer.save(user=review_user, watchlist=watchlist)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)



class ReviewDetailView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    """API view for retrieving Review object"""
    serializer_class = ReviewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly|IsAdminUser,)
    lookup_field = 'id'
    lookup_url_kwarg = 'review_pk'

    # def get_permissions(self):
    #     permissions = {
    #         'POST': [IsAuthenticated()],
    #         'PUT': [IsAuthenticated()],
    #         'DELETE': [IsAuthenticated()],
    #         'GET': [AllowAny()],
    #     }
    #     return permissions.get(self.request.method, [AllowAny()])

    def get_queryset(self):
        watch_pk = self.kwargs.get('watch_pk')
        return Review.objects.filter(watchlist=watch_pk)

    def perform_update(self, serializer):
        watch_pk = self.kwargs.get('watch_pk')
        watchlist = get_object_or_404(WatchList, pk=watch_pk)
        serializer.save(watchlist=watchlist)

    def perform_destroy(self, instance):
        watch_pk = self.kwargs.get('watch_pk')
        get_object_or_404(WatchList, pk=watch_pk)
        instance.delete()

    # def get_object(self):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     review_pk = self.kwargs.get('review_pk')
    #     obj = generics.get_object_or_404(queryset, id=review_pk)
    #     self.check_object_permissions(self.request, obj)
    #     return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class WatchListView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """API view for listing Movie object"""
    serializer_class = WatchListSerializer
    authentication_classes = (TokenAuthentication,) # JWTAuthentication
    permission_classes = (IsAdminOrReadOnly,)
    throttle_scope = 'burst'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filterset_fields = ('active','platform__name',)
    search_fields = ('user__name', 'platform__name',)
    ordering_fields = ('user__name', 'platform__name', 'title')
    pagination_class = WatchListPagination
    ordering = ('title',)

    def get_queryset(self):
        queryset = WatchList.objects.all()
        # platform_name = self.request.query_params.get('platform_name')
        # print(platform_name)
        # if platform_name:
        #     queryset = queryset.filter(platform__name=platform_name)
        return queryset

    # def get_permissions(self):
    #     permissions = {
    #         'POST': [IsAuthenticated()],
    #         'GET': [AllowAny()],
    #     }
    #     return permissions.get(self.request.method, [AllowAny()])

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WatchListDetailView(APIView):
    """API view for retrieving, changing and deleting Movie object"""
    serializer_class = WatchListSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    # def get_permissions(self):
    #     permissions = {
    #         'POST': [IsAuthenticated()],
    #         'PUT': [IsAuthenticated()],
    #         'DELETE': [IsAuthenticated()],
    #         'GET': [AllowAny()],
    #     }
    #     return permissions.get(self.request.method, [AllowAny()])

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
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
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


class StreamingPlatformViewSet(viewsets.ModelViewSet):
    """API view for listing and managing Streaming Platform objects"""
    serializer_class = StreamingPlatformSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    queryset = StreamingPlatform.objects.all().order_by('id')

    def perform_create(self, serializer):
        """Save the user creating the object."""
        serializer.save(user=self.request.user)


# class StreamingPlatformListView(APIView):
#     """API view for retrieving and creating StreamingPlarformView object by id"""
#     serializer_class = StreamingPlatformSerializer
#     authentication_classes = (BasicAuthentication,)
#     permission_classes = (IsAuthenticated,)
#
#     def get_permissions(self):
#         permissions = {
#             'POST': [IsAuthenticated()],
#             'PUT': [IsAuthenticated()],
#             'DELETE': [IsAuthenticated()],
#             'GET': [AllowAny()],
#         }
#         return permissions.get(self.request.method, [AllowAny()])
#
#     def get(self, request, format=None):
#         streaming_platform_list = StreamingPlatform.objects.all().order_by('name')
#         serializer = self.serializer_class(streaming_platform_list, many=True, context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StreamingPlatformDetailView(APIView):
#     """API view for retrieving, changing and deleting StreamingPlatformView object"""
#     serializer_class = StreamingPlatformSerializer
#     authentication_classes = (BasicAuthentication,)
#     permission_classes = (IsAuthenticated,)
#
#     def get_permissions(self):
#         permissions = {
#             'POST': [IsAuthenticated()],
#             'PUT': [IsAuthenticated()],
#             'DELETE': [IsAuthenticated()],
#             'GET': [AllowAny()],
#         }
#         return permissions.get(self.request.method, [AllowAny()])
#
#     def get(self, request, pk, format=None):
#         try:
#             platform = StreamingPlatform.objects.get(pk=pk)
#         except StreamingPlatform.DoesNotExist:
#             return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.serializer_class(platform)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def put(self, request, pk, format=None):
#         try:
#             platform = StreamingPlatform.objects.get(pk=pk)
#         except StreamingPlatform.DoesNotExist:
#             return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.serializer_class(platform, data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         try:
#             platform = StreamingPlatform.objects.get(pk=pk)
#         except StreamingPlatform.DoesNotExist:
#             return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
#         platform.delete(user=request.user)
#         return Response(status=status.HTTP_204_NO_CONTENT)


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
