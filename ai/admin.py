from django.contrib import admin
from .models import Document, DocumentChunk, VectorEmbedding, Conversation, ConversationMessage, Organization, Judge, Case, AuditLog

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'organization', 'file_type', 'total_pages', 'created_at']
    list_filter = ['file_type', 'organization', 'created_at']
    search_fields = ['title', 'user__email', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'page_number', 'start_char', 'end_char']
    list_filter = ['document', 'page_number']
    search_fields = ['chunk_text', 'document__title']
    readonly_fields = ['id', 'created_at']

@admin.register(VectorEmbedding)
class VectorEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['chunk', 'created_at']
    readonly_fields = ['id', 'embedding', 'created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_type', 'query_mode', 'confidence', 'created_at']
    list_filter = ['message_type', 'query_mode', 'response_format', 'created_at']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['id', 'created_at']

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']

@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'court', 'jurisdiction', 'created_at']
    list_filter = ['court', 'jurisdiction']
    search_fields = ['name', 'court']
    readonly_fields = ['id', 'created_at']

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'case_number', 'judge', 'organization', 'outcome', 'created_at']
    list_filter = ['organization', 'judge', 'outcome', 'created_at']
    search_fields = ['title', 'case_number']
    readonly_fields = ['id', 'created_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'timestamp']
    list_filter = ['organization', 'timestamp']
    search_fields = ['user__email', 'query']
    readonly_fields = ['id', 'timestamp']