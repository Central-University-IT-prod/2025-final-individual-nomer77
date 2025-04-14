from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class HeaderLimitOffsetPagination(LimitOffsetPagination):

    def get_paginated_response(self, data):
        response = Response(data)
        response['X-Total-Count'] = self.count
        return response
