from django.contrib import admin
# from .models import UploadChunk,UploadedFiles,ImportFile
# # Register your models here.
from .models import *

# admin.site.register(UploadedFiles)
# admin.site.register(UploadChunk)
# admin.site.register(ImportFile)

admin.site.register(File)
admin.site.register(FileChunk)