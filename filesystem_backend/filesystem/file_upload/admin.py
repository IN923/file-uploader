from django.contrib import admin
from .models import UploadChunk,UploadedFiles,ImportFile
# Register your models here.

admin.site.register(UploadedFiles)
admin.site.register(UploadChunk)
admin.site.register(ImportFile)
