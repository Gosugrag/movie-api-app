from rest_framework.pagination import (PageNumberPagination,
                                       LimitOffsetPagination, CursorPagination)


class WatchListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 20


class WatchListLOPagination(LimitOffsetPagination):
    default_limit = 5
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 20


class WatchListCursorPagination(CursorPagination):
    page_size = 5
    cursor_query_param = 'record'
    ordering = '-created_at'
