from django.db import models
from accounts.models import User

# Create your models here.
class ProtectedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)
    protected_file = models.FileField(upload_to='protected_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ProtectedPDF {self.id} - User: {self.user.email}'


class MergedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merged_file = models.FileField(upload_to='merged_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email}_{self.created_at.strftime("%Y%m%d%H%M%S")}.pdf'


class CompressedPDF(models.Model):
    COMPRESSION_CHOICES = [
        ('extreme', 'Extreme Compression - Less quality, high compression'),
        ('recommended', 'Recommended Compression - Good quality, good compression'),
        ('less', 'Less Compression - High quality, less compression'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    compressed_file = models.FileField(upload_to='compressed_pdfs/')
    compression_quality = models.CharField(max_length=20, choices=COMPRESSION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}_{self.created_at.strftime("%Y%m%d%H%M%S")}_compressed.pdf'


class SplitPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_page = models.IntegerField()
    end_page = models.IntegerField()
    split_pdf = models.FileField(upload_to='split_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Split PDF {self.id}"

class PDFImageConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zip_file = models.FileField(upload_to='pdf_images/zips/', null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True) 


class WordToPdfConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word_to_pdfs = models.ManyToManyField('WordToPdf', related_name='word_to_pdfs')
    created_at = models.DateTimeField(auto_now_add=True)

class WordToPdf(models.Model):
    word_to_pdf = models.FileField(upload_to='word_to_pdf/', null=True, blank=True)


class OrganizedPdf(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organize_pdf = models.FileField(upload_to='organized_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)


class UnlockPdf(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unlock_pdf = models.FileField(upload_to='unlock_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)