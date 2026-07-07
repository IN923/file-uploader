# # routing.py

from django.urls import re_path,path
from .consumers import *

websocket_urlpatterns = [
    # re_path(
    #     r"ws/progress/(?P<job_id>\d+)/$",
    #     ProgressConsumer.as_asgi()
    # ),
    path(r"test/<task_id>/", TestConsumer.as_asgi()),
    path(r"ws/progress/<uname>/",ProgressConsumer.as_asgi()),
]

# print(websocket_urlpatterns)

