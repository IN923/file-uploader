from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from http.client import IncompleteRead
from django.conf import settings
from django.core.files import File as DjangoFile
from .models import *
import pickle
import os
import io
import shutil
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from googleapiclient.errors import HttpError
from requests.exceptions import RequestException


DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive"]
# DOWNLOAD_FOLDER_ID="1dcF80lijoV2dWfJtDcMvHDvYNM9JTkdG"
UPLOAD_FOLDER_ID="1Te73abx9QJQPNbUZj4ttX4Gdievx1QfV"

class GDrive_API:

    def __init__(self):
        self.creds = None
        path = r'/mnt/c/Users/inder.DESKTOP-CFTSNU2/Desktop/company assignment/filesystem_backend/filesystem'
        filepath = os.path.join(path,'token.pickle')
        print(f'path={filepath}',os.path.exists(filepath))

        if os.path.exists(filepath):
            print("file exists")
            with open(filepath,'rb') as token:
                print("file exists11111")
                self.creds = pickle.load(token)
                print("creds scope=",self.creds.scopes,self.creds.valid)

        print("credentails")
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',DRIVE_SCOPE)
                self.creds = flow.run_local_server(port=0)

        with open('token.pickle','wb') as token:
            pickle.dump(self.creds,token)

        self.build_drive_service()

    def build_drive_service(self):
        self.drive_service = None
        if self.creds:
            self.drive_service = build('drive','v3',credentials=self.creds)

    def getFileList(self,download_folder_id):
        print("download_folder_id=",download_folder_id)
        if not self.drive_service or not download_folder_id:
            return
        
        self.files = []
        query = f"'{download_folder_id}' in parents and trashed=false"
        
        while True:
            results = self.drive_service.files().list(q=query,fields="nextPageToken,files(id,name,mimeType,size)",pageSize=100).execute()
            file_list = results.get('files',[])
            self.files.extend(file_list)

            if not results.get('nextPageToken',None):
                break


    def filesUpload(self,filename,file_unique_name,socketname):
        try:
            print("filepath===================",filename)
            saved_file_ref = File.objects.filter(unique_name=file_unique_name).first()
            print(f"saved file reference={saved_file_ref}")
            filepath = os.path.join(settings.BASE_DIR,'media',filename)
            print("filepath===================",filepath)
            if os.path.exists(filepath):
                file_metadata = {'name':filename}
                total_file_size = os.path.getsize(filepath)
                if UPLOAD_FOLDER_ID:
                    file_metadata['parents']=[UPLOAD_FOLDER_ID]

                # media = MediaFileUpload(filepath,resumable=True,chunksize=26214400)
                chunksize=1024*256
                media = MediaFileUpload(filepath,resumable=True,chunksize=chunksize)
                request = self.drive_service.files().create(body=file_metadata,media_body=media,fields='id')
                print("request obj=",request)
                response = None
                retries = 0
                max_retries = 3
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                                f'{socketname}',{
                                'type':'progress.update',
                                'data':{
                                    'file_unique_name':f'{file_unique_name}',
                                    'progress':0,
                                    'uploaded':0,
                                    'total':0,
                                    'progress_status':'pending'
                                    }
                                    })
                uploadedbytes=0
                while not response:
                    try:
                        status,response = request.next_chunk()
                        if status:
                            print(f"iiiiiii status={status},response={response}")
                            progress = int(status.progress()*100)
                            print(f"Upload progress:{progress},{status.resumable_progress}")
                            uploadedbytes = status.resumable_progress
                            async_to_sync(channel_layer.group_send)(
                                f'{socketname}',{
                                'type':'progress.update',
                                'data':{
                                    'file_unique_name':f'{file_unique_name}',
                                    'progress':f'{progress}',
                                    'uploaded':uploadedbytes,
                                    'total':0,
                                    'progress_status':'In progress'
                                    }
                                    })
                            print("update Sent")
                    except (HttpError, RequestException, TimeoutError) as e:
                        print("chunk failed",e)

                        if retries<max_retries:
                            retries+=1
                            wait = min(retries**2,30)
                            time.sleep(wait)

                async_to_sync(channel_layer.group_send)(
                                f'{socketname}',{
                                'type':'progress.update',
                                'data':{
                                    'file_unique_name':f'{file_unique_name}',
                                    'progress':100,
                                    'uploaded':total_file_size,
                                    'total':0,
                                    'progress_status':'COMPLETED'
                                }
                                    })
                print("response obj=",response)
                saved_file_ref.status="completed"
                saved_file_ref.save()
        except Exception as e:
            saved_file_ref.status="failed"
            saved_file_ref.save()

    def filesDownload(self,file,download_folder_id=None):
        try:
            saved_file_ref = File.objects.filter(unique_name=file.get('file_unique_name')).first()
            print("got downloaded got downloaded got downloaded got downloaded",file,File.objects.filter(unique_name=file.get('file_unique_name')))
            if not saved_file_ref:
                print("fileid=",file.get('gfile_id'))
                return 
        
            request = self.drive_service.files().get_media(fileId=file.get('gfile_id'))

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh,request,chunksize=26214400)
            # print("downloader=",downloader.next_chunk())
            done = False
            retries=0
            max_retries=3

            while not done:
                try:
                    status,done = downloader.next_chunk()
                    print(f"progress={status.progress()*100}%")
                except IncompleteRead:
                    retries += 1

                    if retries>max_retries:
                        raise Exception("Download failed after retries")

                    wait = min(retries**2,30)
                    time.sleep(wait)

                    continue

                retries = 0

            fh.seek(0)

            stored_file = DjangoFile(fh)
            stored_file.name = saved_file_ref.name
            saved_file_ref.file = stored_file
            saved_file_ref.save()

            # with open(file_metadata.get('name'),'wb') as f:
            #     shutil.copyfileobj(fh,f)

            print("File Download")

            return saved_file_ref.file.name
        except Exception as e:
            print("error in file download=",e)
            saved_file_ref.status='failed'
            saved_file_ref.save()

    



