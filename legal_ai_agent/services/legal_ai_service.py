import openai
from django.conf import settings


class LegalAIService:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    def get_response(self, messages):
        """
        Return the full GPT response (no streaming)
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        return response.choices[0].message.content
