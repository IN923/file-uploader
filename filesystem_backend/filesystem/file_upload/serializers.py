from rest_framework import serializers
from .models import UploadedFiles,UploadChunk

class UploadedFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFiles
        fields = ['filename','file_size','total_chunks','uploaded_chunks','created_at','mime_type']

    def validate_filename(self,value):
        data = value.split('.')
        if len(data)!=2:
            return serializers.ValidationError('Invalid filename.check file extension.')

        return value

class UploadChunkSerializer(serializers.ModelSerializer):
    uploadfile = serializers.PrimaryKeyRelatedField(queryset=UploadedFiles.objects.all())
    class Meta:
        model = UploadChunk
        fields = ['uploadfile','chunk_number','chunk_path']
