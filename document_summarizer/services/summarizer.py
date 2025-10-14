from django.conf import settings
from .prompt_builder import SummaryPromptBuilder
from .gpt_client import call_gpt_api

class DocumentSummarizer:
    
    @staticmethod
    def create_summary_prompt(text, settings_dict):
        """Create prompt for document summarization using advanced prompt builder"""
        return SummaryPromptBuilder.build_prompt(text, settings_dict)
    
    @staticmethod
    def generate_summary(text, settings_dict=None):
        """Generate AI summary using OpenAI"""
        if not settings_dict:
            settings_dict = {}
            
        try:
            prompt = DocumentSummarizer.create_summary_prompt(text, settings_dict)
            
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful document summarizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                'summary': summary,
                'word_count': len(summary.split()),
                'settings_used': settings_dict
            }
            
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")