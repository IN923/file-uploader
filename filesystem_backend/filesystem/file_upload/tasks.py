from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from .models import ImportFile, ImportJob
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.exceptions import SoftTimeLimitExceeded
import os
import uuid
import pickle

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service_fordownload():
    # path = os.path.join(settings.BASE_DIR, "service_account.json")
    # path = os.path.join(settings.BASE_DIR, "client_secret.json")
    # credentials = service_account.Credentials.from_service_account_file(
    #     path, scopes=DRIVE_SCOPES
    # )
    # return build("drive", "v3", credentials=credentials)
    path = os.path.join(settings.BASE_DIR, "token.pickle")
    with open(path,'rb') as token:
        credentials = pickle.load(token)
    return build("drive", "v3", credentials=credentials)

def _get_drive_service_forupload():
    path = os.path.join(settings.BASE_DIR, "client_secret.json")
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)
    return build("drive", "v3", credentials=credentials)

def _send_progress(file_id,job_id, stage, progress, filename, status="in_progress"):
    # cache_key = f"job_progress_{job_id}"
    print(f"job_id={job_id},stage={stage},progress={progress},filename={filename},status={status}")
    job_data = {}

    # job_data = {
    #     "job_id":job_id,
    #     "stage": stage,
    #     "progress": progress,
    #     "filename": filename
    # }

    # total = job_data.get("total_files", 1)
    # completed = sum(1 for f in files.values() if "status" == "completed")
    # failed = sum(1 for f in files.values() if f["status"] == "error")
    job_data["id"] = file_id
    job_data["progress"] = progress
    job_data["filename"] = filename
    job_data["stage"] = stage
    job_data["job_id"]=job_id
    job_data["status"]=status
    # if failed:
    #     job_data["status"] = "error"
    # elif completed >= total:
    #     job_data["status"] = "completed"
    # else:
    #     job_data["status"] = "in_progress"

    # cache.set(cache_key, job_data, timeout=3600)

    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"job_{job_id}",
            {"type": "progress_update", "data": job_data},
        )


@shared_task(soft_time_limit=1800,time_limit=3000)
def download_file(job_id, folder_id, file_id, filename):
    try:
        drive_service = _get_drive_service_fordownload()
        request = drive_service.files().get_media(fileId=file_id)
        media_path = os.path.join(settings.BASE_DIR, "media", "downloads")
        os.makedirs(media_path, exist_ok=True)

        extns_type = filename.split(".")[-1]
        unique_filename_id = uuid.uuid4()
        filepath = os.path.join(
            settings.BASE_DIR, "media", "downloads", f"{unique_filename_id}.{extns_type}"
        )

        job = ImportJob.objects.get(id=job_id)
        saved_file_reference = ImportFile.objects.create(
            job=job,
            status="PENDING",
            folder_url=folder_id,
            filename=filename,
            unique_id=unique_filename_id,
        )

        try:
            with open(filepath, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                print("donnnnnnnnnniiiiiiiiii",downloader)
                while not done:
                    status, done = downloader.next_chunk()
                    print("down2222222222222222:",done)
                    # if status:
                    #     print("download progress=",status.progress())
                    #     progress = int(status.progress() * 100)
                    #     print("progress=====",progress)
                    #     _send_progress(job_id, "download", progress, filename)

            upload_service = _get_drive_service_forupload()
            upload_folder_id = "1Te73abx9QJQPNbUZj4ttX4Gdievx1QfV"

            file_metadata = {
                "name": filename,
                "parents": [upload_folder_id],
            }

            media_dest = MediaFileUpload(
                filepath,
                mimetype="application/octet-stream",
                resumable=True,
                chunksize=26214400,
            )

            file_request = upload_service.files().create(
                body=file_metadata,
                media_body=media_dest,
                fields="id",
            )

            response = None
            while response is None:
                status, response = file_request.next_chunk()
                print("response rrrrrrrrrr=",response)
                if status:
                    print("upload progress=",status.progress(),response)
                    file_id=response.get("id")
                    progress = int(status.progress() * 100)
                    _send_progress(file_id,id,job_id, "upload", progress, filename)
                    # pass

            saved_file_reference.status = "COMPLETED"
            saved_file_reference.save()
            _send_progress(file_id,job_id, "upload", 100, filename, status="completed")

        except Exception as exc:
            saved_file_reference.status = "FAILED"
            saved_file_reference.save()
            _send_progress(file_id,job_id, "error", 0, filename, status="error")
            raise
    except SoftTimeLimitExceeded:
        print("soft time limit exceeded")
