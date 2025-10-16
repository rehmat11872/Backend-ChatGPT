class SummaryPromptBuilder:
    
    FORMAT_TEMPLATES = {
        'irac': """
Format your response using IRAC structure:
- Issue: What legal issues are presented?
- Rule: What legal rules/principles apply?
- Analysis: How do the rules apply to the facts?
- Conclusion: What is the outcome/recommendation?
        """,
        'executive': """
Format as an Executive Summary with:
- Executive Overview (2-3 sentences)
- Key Findings
- Recommendations
- Next Steps
        """,
        'detailed': """
Format as a Detailed Analysis with:
- Background/Context
- Main Points (numbered)
- Supporting Evidence
- Implications
- Conclusions
        """,
        'bullet_points': """
Format as clear bullet points:
- Use • for main points
- Use - for sub-points
- Keep each point concise
- Group related information
        """
    }
    
    @staticmethod
    def build_prompt(text, settings):
        """Build GPT prompt based on user settings"""
        
        # Extract settings with defaults
        format_type = settings.get('format', 'bullet_points')
        summary_length = settings.get('summary_length', 50)  # percentage
        confidence_threshold = settings.get('confidence_threshold', 80)  # percentage
        inclusions = settings.get('inclusions', ['facts', 'issues'])
        citation_style = settings.get('citation_style', 'none')
        language = settings.get('language', 'english')
        
        # Build prompt sections
        prompt_parts = []
        
        # System instruction
        prompt_parts.append(f"You are a professional document summarizer. Respond in {language}.")
        
        # Length instruction
        length_instruction = f"Create a summary that is approximately {summary_length}% of the original length."
        prompt_parts.append(length_instruction)
        
        # Format instruction
        format_template = SummaryPromptBuilder.FORMAT_TEMPLATES.get(format_type, SummaryPromptBuilder.FORMAT_TEMPLATES['bullet_points'])
        prompt_parts.append(format_template)
        
        # Inclusions instruction
        if inclusions:
            inclusion_text = ", ".join(inclusions)
            prompt_parts.append(f"Focus specifically on: {inclusion_text}")
        
        # Confidence instruction
        if confidence_threshold > 0:
            prompt_parts.append(f"Only include information you are {confidence_threshold}% confident about. Mark uncertain information with '[uncertain]'.")
        
        # Citation instruction
        if citation_style != 'none':
            prompt_parts.append(f"Include citations in {citation_style} format where applicable.")
        
        # Document text
        prompt_parts.append(f"\nDocument to summarize:\n{text}\n")
        prompt_parts.append("Summary:")
        
        return "\n\n".join(prompt_parts)