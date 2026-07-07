from django.db import models
# Create your models here.

# class UploadedFiles(models.Model):
#     filename = models.CharField(null=True)
#     file_size = models.BigIntegerField(default=0)
#     total_chunks = models.IntegerField(null=True)
#     uploaded_chunks = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     # file_path = models.FileField(upload_to="uploads",)
#     google_file_id = models.CharField(max_length=255, unique=True,null=True)
#     mime_type = models.CharField(max_length=255, blank=True, null=True)
#     # web_view_link = models.URLField(blank=True, null=True)

# class UploadChunk(models.Model):
#     uploadfile = models.ForeignKey(UploadedFiles,on_delete=models.CASCADE)
#     chunk_number = models.IntegerField()
#     chunk_path = models.FileField(upload_to="django uploads",null=True)

# # Solution 1: Use a Shared Drive (Best for service accounts)

# # If you have a Google Workspace account:

# # Create a Shared Drive.
# # Copy the service account email from your JSON file:
# # "client_email": "xxxxx@filesystem-gdrive.iam.gserviceaccount.com"
# # Add that email as a member of the Shared Drive.
# # Give it Content Manager permissions.
# # Configure your storage backend to upload into that Shared Drive/folder.

# class ImportJob(models.Model):

#     STATUS_CHOICES = (
#         ('PENDING', 'PENDING'),
#         ('PROCESSING', 'PROCESSING'),
#         ('COMPLETED', 'COMPLETED'),
#         ('FAILED', 'FAILED'),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='PENDING'
#     )
#     created_at = models.DateTimeField(auto_now_add=True,null=True)

# class ImportFile(models.Model):
#     STATUS_CHOICES = (
#         ('PENDING','PENDING'),
#         ('PROCESSING','PROCESSING'),
#         ('COMPLETED','COMPLETED'),
#         ('FAILED','FAILED'),
#     )

#     folder_url = models.URLField()
#     status = models.CharField(max_length=20)
#     total_bytes = models.BigIntegerField(default=0)
#     filename =models.FileField(null=True)
#     unique_id = models.UUIDField(null=True)
#     job = models.ForeignKey(ImportJob,on_delete=models.CASCADE,related_name='files')
#     # processed_bytes = models.BigIntegerField(default=0)
#     # destination = models.FileField(null=True)


class File(models.Model):
    STAGE_CHOICES = [
        ('download','DOWNLOAD'),
        ('upload','UPLOAD'),
        ('migrate','MIGRATE')
    ]

    STATUS = [
        ('pending','PENDING'),
        ('completed','COMPLETED'),
        ('failed','FAILED')
    ]

    name = models.CharField(max_length=225)
    created_at = models.DateTimeField(auto_now_add=True)
    unique_name = models.UUIDField(unique=True)
    # source = models.URLField()
    stage = models.CharField(choices=STAGE_CHOICES)
    file = models.FileField(upload_to='uploads',null=True)
    total_chunks = models.PositiveIntegerField(default=0)
    status=models.CharField(choices=STATUS,default='pending')


class FileChunk(models.Model):
    file = models.ForeignKey(File,on_delete=models.CASCADE,null=True)
    chunk_number = models.PositiveIntegerField()
    chunk_file = models.FileField(upload_to='uploads',null=False)
    # unique_name = models.UUIDField(unique=True,null=True)
    # total_bytes = models.IntegerField()


# class Jobs(models.Model):

    
