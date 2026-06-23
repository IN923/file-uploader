# # routing.py

from django.urls import re_path,path
from .consumers import ProgressConsumer,TestConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/progress/(?P<job_id>\d+)/$",
        ProgressConsumer.as_asgi()
    ),
    path(r"test/", TestConsumer.as_asgi()),
]

# print(websocket_urlpatterns)

