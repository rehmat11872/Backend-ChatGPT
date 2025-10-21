from django.db import models
from accounts.models import User

class UploadedDocument(models.Model):
    SUPPORTED_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('txt', 'TXT'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=SUPPORTED_TYPES)
    file_size = models.BigIntegerField()  # in bytes
    file_path = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.user.email}"