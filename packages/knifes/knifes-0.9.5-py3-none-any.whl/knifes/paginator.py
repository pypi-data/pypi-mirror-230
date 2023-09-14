import math
from django.db.models import QuerySet
from dataclasses import dataclass


class Pagination:
    def __init__(self, current_page, page_size, total_size):
        self.current_page = current_page if current_page >= 1 else 1  # 从第1页开始
        self.page_size = page_size if page_size >= 1 else 1  # 避免出现<1的情况
        self.total_size = total_size
        self.total_page = math.ceil(self.total_size / self.page_size)


@dataclass
class PageData:
    items: list
    pagination: Pagination


def paginate(current_page, page_size, queryset: QuerySet):
    pagination = Pagination(current_page, page_size, queryset.count())
    slice_begin = (pagination.current_page - 1) * pagination.page_size
    slice_end = pagination.current_page * pagination.page_size
    return PageData(items=queryset[slice_begin: slice_end], pagination=pagination)



