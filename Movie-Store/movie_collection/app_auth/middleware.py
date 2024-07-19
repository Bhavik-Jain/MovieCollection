from django.db import transaction
from .models import RequestCount


class RequestCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with transaction.atomic():
            counter = RequestCount.objects.select_for_update().first()
            counter.count += 1
            counter.save()
        response = self.get_response(request)
        return response

    @staticmethod
    def get_request_count():
        count_of_requests = RequestCount.objects.first().count
        print(count_of_requests)
        return count_of_requests

    @staticmethod
    def reset_request_count():
        counter = RequestCount.objects.first()
        counter.count = 0
        counter.save()
