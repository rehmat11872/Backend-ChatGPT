from django.db import models
from accounts.models import User

# Create your models here.

class PromptSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='user_uploads/', blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.prompt[:20]}'
