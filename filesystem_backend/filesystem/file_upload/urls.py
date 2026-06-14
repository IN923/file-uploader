from django.urls import path
from .views import handle_filechunks,merge_file

urlpatterns = [
    path('filechunk/',handle_filechunks),
    path('filemerge/',merge_file),
]

