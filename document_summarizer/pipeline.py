"""
Document summarization pipeline - orchestrates the entire flow
Input: text and settings
Output: complete summary with download link
Dependencies: prompt_builder, gpt_client, response_utils
"""
from .services.prompt_builder import SummaryPromptBuilder
from .services.gpt_client import call_gpt_api
from .response_utils import create_download_link

def validate_input(text, settings):
    """Validate text size and settings before processing"""
    if len(text) > 100000:  # 100k chars max
        raise ValueError("Text too long. Maximum 100,000 characters allowed.")
    
    if not text.strip():
        raise ValueError("Text cannot be empty.")
    
    return True

def generate_summary(text, settings, request):
    """Main pipeline: validate → build prompt → call GPT → format response"""
    
    # Step 1: Validate input
    validate_input(text, settings)
    
    # Step 2: Build prompt
    prompt = SummaryPromptBuilder.build_prompt(text, settings)
    
    # Step 3: Call GPT
    gpt_result = call_gpt_api(prompt, text)
    
    # Step 4: Prepare summary data
    summary_data = {
        'summary': gpt_result['summary'],
        'word_count': len(gpt_result['summary'].split()),
        'settings_used': settings,
        'tokens_used': gpt_result.get('tokens_used'),
        'model': gpt_result.get('model', 'gpt-3.5-turbo')
    }
    
    # Step 5: Create download link
    download_info = create_download_link(summary_data, request)
    
    # Step 6: Return complete response
    return {**summary_data, **download_info}