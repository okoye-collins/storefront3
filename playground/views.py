from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import  Response
from .tasks import notify_customers
import requests
import logging

logger = logging.getLogger(__name__)

class HelloView(APIView):
    # @method_decorator(cache_page(5 * 60))
    def get(self, request):
        try:
            logger.info('Caling httpbin')
            response = requests.get("https://httpbin.org/delay/2")
            logger.info('Received the response')
            data = response.json()
        except requests.ConnectionError:
            logger.critical('Httpbin is offline')
        return render(request, "hello.html", {"name": "collins"}) 

# @cache_page(5 * 60)
# def say_hello(request):
#     # notify_customers.delay('Hello')
#     response = requests.get("https://httpbin.org/delay/2")
#     data = response.json()
#     return render(request, "hello.html", {"name": "collins"})
