from rest_framework import pagination, response


class RestPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'per_page'
    # max_page_size = 100

    def get_paginated_response(self, data):

        # Get id's of records in current page
        # firstRecord = data[0]['id'] if (data and 'id' in data[0]) else None
        # lastRecord = data[-1]['id'] if (data and 'id' in data[0]) else None

        return response.Response({
            'total': self.page.paginator.count,
            'per_page': self.get_page_size(self.request),
            'current_page': int(self.request.query_params.get('page', 1)),
            'last_page': int(self.page.paginator.num_pages),
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            # 'first': firstRecord,
            # 'last': lastRecord,
            'results': data
        })


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'per_page'
    # max_page_size = 100

    def get_paginated_response(self, data):

        # Get id's of records in current page
        # firstRecord = data[0]['id'] if (data and 'id' in data[0]) else None
        # lastRecord = data[-1]['id'] if (data and 'id' in data[0]) else None

        return response.Response({
            'total': self.page.paginator.count,
            'per_page': self.get_page_size(self.request),
            'current_page': self.request.query_params.get('page', 1),
            'last_page': self.page.paginator.num_pages,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            # 'first': firstRecord,
            # 'last': lastRecord,
            'results': data
        })


class PaginationHandlerMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                                                self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

class JMeterPagination(pagination.PageNumberPagination):
    page_size = 1
    page_size_query_param = 'per_page'
    # max_page_size = 100

    def get_paginated_response(self, data):

        # Get id's of records in current page
        # firstRecord = data[0]['id'] if (data and 'id' in data[0]) else None
        # lastRecord = data[-1]['id'] if (data and 'id' in data[0]) else None

        return response.Response({
            'total': self.page.paginator.count,
            'per_page': self.get_page_size(self.request),
            'current_page': self.request.query_params.get('page', 1),
            'last_page': self.page.paginator.num_pages,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            # 'first': firstRecord,
            # 'last': lastRecord,
            'results': data
        })