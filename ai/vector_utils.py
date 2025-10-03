import openai
import numpy as np
from django.conf import settings
from .models import DocumentChunk, VectorEmbedding
import json

class VectorProcessor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def chunk_text(self, text, chunk_size=1000, overlap=100):
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            chunks.append({
                'text': chunk,
                'start_char': start,
                'end_char': end
            })
            
            start = end - overlap
            
        return chunks
    
    def create_embedding(self, text):
        """Create vector embedding using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def store_document_chunks(self, document, text_content):
        """Process and store document chunks with embeddings"""
        chunks = self.chunk_text(text_content)
        
        for i, chunk_data in enumerate(chunks):
            # Create document chunk
            chunk = DocumentChunk.objects.create(
                document=document,
                chunk_text=chunk_data['text'],
                chunk_index=i,
                start_char=chunk_data['start_char'],
                end_char=chunk_data['end_char']
            )
            
            # Create embedding
            embedding = self.create_embedding(chunk_data['text'])
            if embedding:
                VectorEmbedding.objects.create(
                    chunk=chunk,
                    embedding=embedding
                )
        
        return len(chunks)
    
    def similarity_search(self, query_text, document_ids=None, top_k=5):
        """Find similar chunks using cosine similarity"""
        query_embedding = self.create_embedding(query_text)
        if not query_embedding:
            return []
        
        # Get all embeddings (filtered by documents if specified)
        embeddings_qs = VectorEmbedding.objects.select_related('chunk__document')
        
        if document_ids:
            embeddings_qs = embeddings_qs.filter(chunk__document__id__in=document_ids)
        
        results = []
        for vec_embed in embeddings_qs:
            similarity = self.cosine_similarity(query_embedding, vec_embed.embedding)
            results.append({
                'chunk': vec_embed.chunk,
                'similarity': similarity,
                'document': vec_embed.chunk.document
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)