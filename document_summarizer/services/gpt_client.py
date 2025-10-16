import openai
import time
from django.conf import settings

openai.api_key = getattr(settings, "OPENAI_API_KEY", None)

def call_gpt_api(prompt, text, model="gpt-3.5-turbo", max_retries=3):
    """
    Calls GPT API with retries and returns summary response.
    """
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal summarization assistant."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                temperature=0.5,
                max_tokens=1500,
            )

            summary_text = response.choices[0].message.content.strip()
            return {
                "summary": summary_text,
                "model": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, "usage") else None,
            }

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"GPT API failed after {max_retries} attempts: {e}")