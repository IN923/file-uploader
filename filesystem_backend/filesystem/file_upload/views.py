from django.shortcuts import render
from django.conf import settings
from django.core.files import File
# from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import UploadChunkSerializer,UploadedFilesSerializer
from .models import UploadedFiles,UploadChunk,ImportJob
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
from google.oauth2 import service_account
from .tasks import download_file

# Create your views here.

@api_view(["POST"])
def handle_filechunks(request):
    print("request data:",request.data)
    uploadfile_id = None
    if request.data.get('uploadfile'):
        uploaded_file = UploadChunkSerializer(data=request.data)
        uploadfile_id = request.data.get('uploadfile')
    media_path = os.path.join(settings.BASE_DIR,'media')
    if not os.path.exists(media_path):
        os.makedirs(media_path)

    chunk_number = request.data.get('chunk_number')
    uploaded_chunk_data = UploadChunk()
    uploaded_chunk_data.chunk_number = chunk_number
    content = request.FILES.get('file')
    print("content2=",content)

    if uploadfile_id:
        try:
            saved_file = UploadedFiles.objects.get(id=uploadfile_id)
        except UploadedFiles.DoesNotExist:
            return Response({"message":"file does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    uploaded_chunk_data.uploadfile = saved_file
    # chunk_path = f'{media_path}/{saved_file.filename}_{chunk_number}'
    filename = saved_file.filename.split('.')[0]
    chunk_path = os.path.join(settings.BASE_DIR,'media',f'{filename}_{chunk_number}.{saved_file.mime_type}')
    print("chunk path:",chunk_path)

    with open(chunk_path,'wb') as file:
        for chunk in content.chunks():
            file.write(chunk)

    uploaded_chunk_data.chunk_path = chunk_path
    uploaded_chunk_data.save()

    return Response({'uploaded_file_id':saved_file.id},status=status.HTTP_201_CREATED)


@api_view(['POST'])
def merge_file(request):
    print("file merge",request.data)
    uploaded_file_id = request.data.get('upload_id')
    try:
        file_data = UploadedFiles.objects.get(id=uploaded_file_id)
    except UploadedFiles.DoesNotExist:
        return Response({'message':'file does not exist'},status=status.HTTP_404_NOT_FOUND)
    
    all_chunks = UploadChunk.objects.filter(uploadfile=file_data).order_by('chunk_number')

    chunk_dir = f"media"
    output_file = file_data.filename
    print("chunk_directory=",os.listdir(chunk_dir))
    with open(output_file, "wb+") as outfile:
        for filename in sorted(
            os.listdir(chunk_dir),
            key=lambda x: int(x.split("_")[-1][0])
        ):
            chunk_path = os.path.join(chunk_dir, filename)

            with open(chunk_path, "rb") as infile:
                outfile.write(infile.read())

    print("credentials checked")
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    service = build('drive', 'v3', credentials=creds)

    folder_id = '1Te73abx9QJQPNbUZj4ttX4Gdievx1QfV'

    media = MediaFileUpload(output_file,resumable=True,chunksize=8 * 1024 * 1024)
    file = service.files().create(
    body={
        "name": file_data.filename,
        "parents": [f"{folder_id}"]
    },media_body=media,fields="id, name, parents,mimeType,size,webViewLink").execute()
    
    # result = None

    # while result is None:
    #     status_code, response = body.next_chunk()

    #     if status_code:
    #         uploaded = status_code.resumable_progress
    #         total = media.size()
    #         percent = uploaded / total * 100

    #     print(
    #         f"{uploaded:,} / {total:,} bytes "
    #         f"({percent:.2f}%)"
    #     )

    print("gdrive file:",file)
    file_data.google_file_id = file.get('id')
    file_data.mime_type = file.get('mime_type')
    file_data.save()

    return Response({"message":"file uploaded succcessfully"},status=status.HTTP_200_OK)

@api_view(['POST'])
def createfile(request):
    print("request data:",request.data)
    uploadfile_id = None

    file_data = UploadedFilesSerializer(data=request.data)
    print("file_data:",file_data,file_data.is_valid())
    print("filedata errors:",file_data.errors)
    if file_data.is_valid():
        ext_type = file_data.validated_data['filename'].split('.')[1]
        saved_file = file_data.save(mime_type=ext_type)
        print("first time:",saved_file.id)
    #     # check if media folder exist or not
    #     media_path = os.path.join(settings.BASE_DIR,'media')
    #     if not os.path.exists(media_path):
    #         os.makedirs(media_path)

    # filename = saved_file.filename.split('.')[0]
    # chunk_path = os.path.join(settings.BASE_DIR,'media',f'{filename}_{chunk_number}.{saved_file.mime_type}')
    # print("chunk path:",chunk_path)


    return Response({'uploaded_file_id':saved_file.id},status=status.HTTP_201_CREATED)




@api_view(["POST"])
def list_files(request):
    print("request data",request.data)
    link = request.data.get('link')
    print("backend link=",link)
    # link = "https://drive.google.com/drive/folders/1dcF80lijoV2dWfJtDcMvHDvYNM9JTkdG"
    folder_id = link.split("/")[-1]
    print("folder_id=",folder_id)

    SCOPES = [
    "https://www.googleapis.com/auth/drive"
]
    print(settings.BASE_DIR)

    path=os.path.join(settings.BASE_DIR,"token.pickle")
    print("list files client json=",path)
    with open(path,'rb') as token:
        credentials = pickle.load(token)

    print("creds",credentials)

    drive_service = build(
    "drive",
    "v3",
    credentials=credentials
    )

    try:
        folder = drive_service.files().get(
            fileId=folder_id,
            fields="id,name"
        ).execute()

        print(folder)

    except Exception as e:
        print(e)

    response = drive_service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id,name,size,mimeType)"
    ).execute()

    files = response.get("files", [])

    for item in files:
        item['status']="pending"

    job = ImportJob.objects.create(status="PENDING")
    # cache.set(
    #     f"job_progress_{job.id}",
    #     {"total_files": len(files), "files": {}, "status": "pending", "progress": 0},
    #     timeout=3600,
    # )

    for file in files:

        file_id = file["id"]
        filename = file["name"]

        download_file.delay(job.id,
            folder_id,
            file_id,
            filename
        )

        print("files data=",files)

    return Response({"job_id": job.id,"files":files})


# @api_view(["GET"])
# def job_progress(request, job_id):
#     progress = cache.get(f"job_progress_{job_id}")
#     if progress is None:
#         return Response({"status": "pending", "progress": 0})
#     return Response(progress)
