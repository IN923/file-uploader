from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.exceptions import SoftTimeLimitExceeded
from django.core.files import File as DjangoFile
# from asgiref.sync import sync_to_async
import os
import uuid
import pickle
import time
import io
import sys
from .utils import *


@shared_task(soft_time_limit=600,time_limit=900)
def MergeFileTask(file_unique_name,socketname):

    try:
        file = File.objects.get(unique_name=file_unique_name)
    except File.DoesNotExist:
        return print("message':'File not found error")

    chunks = FileChunk.objects.filter(file=file).order_by('chunk_number')

    with io.BytesIO() as file_collection:
        for filechunk in chunks:
            print(f"chunk Number={filechunk.chunk_number},length file={filechunk.chunk_file.size}")
            with open(filechunk.chunk_file.path,'rb') as f:
                print("types of file obj=",type(f),type(file_collection))
                file_content = f.read()

                file_collection.write(file_content)

        file_collection = DjangoFile(file_collection)
        file_collection.name = file.name
        file.file = file_collection
        file.save()

        if file.file.size>1000000000:
            async_to_sync(channel_layer.group_send)(
                f'{socketname}',{
                    'type':'progress.update',
                    'data':{
                        'file_unique_name':f'{file_unique_name}',
                        'progress':0,
                        'uploaded':0,
                        'total':0,
                        'progress_status':'FAILED'
                        }
                        })
            file.status = 'failed'
            file.save()
            raise Exception("file size is greater than 1GB")

        print("file emrging done iiiiiiiiiii")
        print("Sending to group:", repr(file.unique_name))
        channel_layer = get_channel_layer()
        print(f'ffffffffff====={socketname}')
        async_to_sync(channel_layer.group_send)(f'{socketname}',{
            'type':'merge.status',
            'msg':'success',
            'filename':file.file.name,
            'socketname':socketname,
            'unique_name':f'{file.unique_name}'})

@shared_task()
def upload_file(socketname,should_download=False,filename=None,file_item=None,download_folder_id=None):
    try:
        GDrive=GDrive_API()
        print(f"filename={filename},file_item={file_item}")
        if should_download:
            print(f"files download==========={should_download},file_item={file_item}oooooo")
            filename = GDrive.filesDownload(file=file_item,download_folder_id=download_folder_id)
            print(f"filename in task celery={filename}")
            GDrive.filesUpload(filename,file_item.get('file_unique_name'),socketname)
        else:
            GDrive.filesUpload(filename,file_item,socketname)
        print("iiiii=",filename)
    except Exception as e:
        pass

