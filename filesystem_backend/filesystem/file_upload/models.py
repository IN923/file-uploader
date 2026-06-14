from django.db import models
# Create your models here.

class UploadedFiles(models.Model):
    filename = models.CharField(null=True)
    file_size = models.BigIntegerField(default=0)
    total_chunks = models.IntegerField(null=True)
    uploaded_chunks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # file_path = models.FileField(upload_to="uploads",)
    google_file_id = models.CharField(max_length=255, unique=True,null=True)
    mime_type = models.CharField(max_length=255, blank=True, null=True)
    # web_view_link = models.URLField(blank=True, null=True)

class UploadChunk(models.Model):
    uploadfile = models.ForeignKey(UploadedFiles,on_delete=models.CASCADE)
    chunk_number = models.IntegerField()
    chunk_path = models.FileField(upload_to="django uploads",null=True)

# Solution 1: Use a Shared Drive (Best for service accounts)

# If you have a Google Workspace account:

# Create a Shared Drive.
# Copy the service account email from your JSON file:
# "client_email": "xxxxx@filesystem-gdrive.iam.gserviceaccount.com"
# Add that email as a member of the Shared Drive.
# Give it Content Manager permissions.
# Configure your storage backend to upload into that Shared Drive/folder.