from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from http.client import IncompleteRead
import pickle
import os
import io
import shutil
import time

DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive"]
DOWNLOAD_FOLDER_ID="1dcF80lijoV2dWfJtDcMvHDvYNM9JTkdG"
UPLOAD_FOLDER_ID="1Te73abx9QJQPNbUZj4ttX4Gdievx1QfV"

def get_or_create_credentials():
    creds = None
    path = r'/mnt/c/Users/inder.DESKTOP-CFTSNU2/Desktop/company assignment/filesystem_backend/filesystem'
    filepath = os.path.join(path,'token.pickle')
    print(f'path={filepath}',os.path.exists(filepath))

    if os.path.exists(filepath):
        print("file exists")
        with open(filepath,'rb') as token:
            print("file exists11111")
            creds = pickle.load(token)
            print("creds scope=",creds.scopes,creds.valid)

    print("credentails")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',DRIVE_SCOPE)
            creds = flow.run_local_server(port=0)

    with open('token.pickle','wb') as token:
        pickle.dump(creds,token)

    return creds

def build_drive_service(creds):
    drive_service = None
    if creds:
        drive_service = build('drive','v3',credentials=creds)

    return drive_service

def getFileList():
    credentials = get_or_create_credentials()
    print("credentails")
    service = build_drive_service(credentials)

    if not service:
        return
    files = []
    query = f"'{DOWNLOAD_FOLDER_ID}' in parents and trashed=false"
    while True:
        results = service.files().list(q=query,fields="nextPageToken,files(id,name,mimeType)",pageSize=100).execute()
        file_list = results.get('files',[])
        files.extend(file_list)

        if not results.get('nextPageToken',None):
            break

    return files

def filesDownload():
    credentials = get_or_create_credentials()
    service = build_drive_service(credentials)
    files = getFileList()

    for file_metadata in files:
        print("fileid=",file_metadata.get('id'))
        request = service.files().get_media(fileId=file_metadata.get('id'))

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

                if reries>max_retries:
                    raise Exception("Download failed after retries")

                wait = (retries**2,30)
                time.sleep(wait)

                continue

            retries = 0

        fh.seek(0)

        with open(file_metadata.get('name'),'wb') as f:
            shutil.copyfileobj(fh,f)

        print("File Download")

        


def filesUpload(filename):
    credentials = get_or_create_credentials()
    service = build_drive_service(credentials)
    path = r'C:\Users\inder.DESKTOP-CFTSNU2\Desktop\company assignment\filesystem_backend\filesystem'
    filepath = os.path.join(path,filename)
    if os.path.exists(filepath):
        file_metadata = {'name':filename}
        
        if UPLOAD_FOLDER_ID:
            file_metadata['parents']=[UPLOAD_FOLDER_ID]

        # try:
        media = MediaFileUpload(filepath,resumable=True,chunksize=26214400)
        request = service.files().create(body=file_metadata,media_body=media,fields='id')
        print("request obj=",request)
        response = None
        retries = 0
        max_retries = 3

        while not response:
            try:
                status,response = request.next_chunk()
                if status:
                    print("Upload progress:",status.progress())
            except (HttpError, RequestException, TimeoutError) as e:
                print("chunk failed",e)

                if retries<max_retries:
                    retries+=1
                    wait = retries**2
                    time.sleep(wait,30)
            print("response obj=",response)

            # print('response file id:',response['id'])
            # return response['id']
        # except Exception as e:
        #     print("exception block:",e)

if __name__=="__main__":
    # print("function call=",filesDownload())
    print(filesUpload("500MB-CZIPtestfile.org.zip"))
