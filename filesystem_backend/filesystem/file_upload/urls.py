from django.urls import path
from .views import handle_filechunks,merge_file,createfile,list_files
# ,job_progress

urlpatterns = [
    path('filechunk/',handle_filechunks),
    path('filemerge/',merge_file),
    path('start/',createfile),
    path("get-files/",list_files),
    # path("job-progress/<int:job_id>/", job_progress),
]

