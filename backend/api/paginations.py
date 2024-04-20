from rest_framework import pagination

from foodgram_backend.constants import MAX_PAGE_SIZE


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE
    page_query_param = 'page'
