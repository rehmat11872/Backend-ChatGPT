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

class UserSettings(models.Model):
    CITATION_CHOICES = [
        ('bluebook', 'Bluebook'),
        ('apa', 'APA'),
        ('mla', 'MLA'),
        ('chicago', 'Chicago'),
    ]
    
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    summary_length = models.IntegerField(default=60)
    confidence_threshold = models.IntegerField(default=75)
    key_facts = models.BooleanField(default=True)
    legal_issues = models.BooleanField(default=True)
    holdings_and_rulings = models.BooleanField(default=True)
    recommendations = models.BooleanField(default=False)
    citation_style = models.CharField(max_length=20, choices=CITATION_CHOICES, default='bluebook')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='english')
    auto_save = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Settings for {self.user.email}"