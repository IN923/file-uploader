from django.shortcuts import render
from django.conf import settings
from django.core.files import File
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from .models import *
from .tasks import *
import os
import pickle
import uuid
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
from google.oauth2 import service_account
from asgiref.sync import sync_to_async
from django.core.files import File as DjangoFile
from django.views.decorators.csrf import csrf_exempt
# from .tasks import download_file

# # Create your views here.

class FileChunkView(APIView):
    def post(self,request):
        print("request data:",request.data)

        file_chunk = FileChunkCreateSerializer(data=request.data)

        if file_chunk.is_valid():
            file_chunk.save()
            return Response({'message':'Chunk saved',})
        print("file chunk errors:",file_chunk.errors)
        return Response(file_chunk.errors)

@csrf_exempt
@api_view(['POST'])
def merge_file_view(request):
    file_unique_name = request.data.get('file_unique_name')

    if not file_unique_name:
        return Response("File uinique name is required.")

    excluded_statuses = ['failed', 'completed']
    try:
        saved_file_ref = File.objects.filter(unique_name=file_unique_name).exclude(status__in=excluded_statuses)
    except File.DoesNotExist:
        return Response("File do not exist")
    
    socketname = request.data.get('socketname')
    print("file_unique_name in merge view =",file_unique_name,socketname)

    MergeFileTask.delay(file_unique_name,socketname)

    return Response({'message':'File uploading in progress'})


@api_view(['POST'])
def createfile(request):
    print("request data:",request.data)
    file_data = FileCreateSerializer(data=request.data)
    if file_data.is_valid():
        saved_file_instance = file_data.save(unique_name=uuid.uuid4(),stage='upload')
        print("file_data =",saved_file_instance.unique_name)
        return Response({'file_unique_name':saved_file_instance.unique_name},status=status.HTTP_201_CREATED)

    return Response(file_data.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def paste_link(request):
    print("request=",request.data)
    url = request.data.get('link')
    socketname = request.data.get('socketname')
    print(f'url={url}')

    if not url:
        return Response({'message':'url field is missing'})
    
    url_folder_id = url.split('/')[-1]

    GDrive = GDrive_API()
    GDrive.getFileList(url_folder_id)
    file_list = GDrive.files
    print("files=",file_list,url_folder_id)
    data = []
    if file_list:
        for file in file_list:
            unique_name = uuid.uuid4()
            file_data = File.objects.create(name=file.get('name'),unique_name=unique_name,stage='migrate')
            print(f"file_data={file_data.unique_name}")

            if int(file.get('size',0))>1000000000:
                continue

            item = {
                'name':file.get('name'),
                'gfile_id':file.get('id'),
                'file_unique_name':f'{file_data.unique_name}',
                'uploaded':0,
                'total':file.get('size',0),
                'progress_status':'pending',
                'progress':0
            }
            data.append(item)

            upload_file.delay(socketname,file_item=item,should_download=True,download_folder_id=url_folder_id)
        return Response(data)
    
    # return Response()