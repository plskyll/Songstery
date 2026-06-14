from rest_framework.pagination import CursorPagination


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"


class BookCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"


class MusicCursorPagination(CursorPagination):
    page_size = 30
    ordering = "-likes_count"
    cursor_query_param = "cursor"


class NotificationCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"
