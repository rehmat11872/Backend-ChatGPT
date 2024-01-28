from django.contrib import admin
from .models import PromptSubmission
# Register your models here.

class PromptSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user',]  
    
admin.site.register(PromptSubmission, PromptSubmissionAdmin)