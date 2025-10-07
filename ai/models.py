from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # Law firm name
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organizations'

class Judge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    court = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'judges'

class Case(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    case_number = models.CharField(max_length=100)
    judge = models.ForeignKey(Judge, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    outcome = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cases'

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    query = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/', blank=True, null=True)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()
    total_pages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_documents'

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(null=True, blank=True)
    start_char = models.IntegerField()
    end_char = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_document_chunks'
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]

class VectorEmbedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk = models.OneToOneField(DocumentChunk, on_delete=models.CASCADE, related_name='embedding')
    embedding = models.JSONField()  # Will store vector as JSON array for now
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_vector_embeddings'

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'

class ConversationMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    query_mode = models.CharField(max_length=50, blank=True)
    response_format = models.CharField(max_length=50, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_conversation_messages'
        ordering = ['created_at']

# Citation Maps Models
class CourtCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    citation = models.CharField(max_length=200, unique=True)
    court = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=100)
    date_decided = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    # Graph algorithm scores
    pagerank_score = models.FloatField(default=0.0)
    betweenness_score = models.FloatField(default=0.0)
    citation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'court_cases'
        indexes = [
            models.Index(fields=['citation']),
            models.Index(fields=['court']),
            models.Index(fields=['jurisdiction']),
        ]

class Citation(models.Model):
    CITATION_TYPES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('distinguished', 'Distinguished'),
        ('overruled', 'Overruled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citing_case = models.ForeignKey(CourtCase, on_delete=models.CASCADE, related_name='citations_made')
    cited_case = models.ForeignKey(CourtCase, on_delete=models.CASCADE, related_name='citations_received')
    citation_type = models.CharField(max_length=20, choices=CITATION_TYPES, default='neutral')
    weight = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'citations'
        unique_together = ['citing_case', 'cited_case']
        indexes = [
            models.Index(fields=['citing_case']),
            models.Index(fields=['cited_case']),
        ]