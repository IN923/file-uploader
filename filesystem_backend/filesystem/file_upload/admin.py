from django.contrib import admin
from .models import UploadChunk,UploadedFiles
# Register your models here.

admin.site.register(UploadedFiles)
admin.site.register(UploadChunk)
