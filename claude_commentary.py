"""
Claude AI commentary generator for weather forecasts.
Uses Anthropic's Claude Haiku 4.5 to generate witty weather comments.
"""

import anthropic
import os
import logging
from typing import Optional


logger = logging.getLogger(__name__)


def generate_weather_comment(weather_data: str, prompt_template: str) -> Optional[str]:
    """
    Generate witty weather comment using Claude Haiku 4.5 API.
    
    Args:
        weather_data: String summary of weather conditions
        prompt_template: Prompt template with {weather_summary} placeholder
        
    Returns:
        Generated comment string, or None if API call fails
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.debug("no ANTHROPIC_API_KEY found, skipping commentary")
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = prompt_template.format(weather_summary=weather_data)
        
        logger.debug(f"calling claude api with prompt: {prompt[:100]}...")
        
        message = client.messages.create(
            model="claude-haiku-4-5",  # Haiku 4.5 model (Oct 2025)
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        comment = message.content[0].text.strip()
        logger.info(f"generated weather comment: {comment}")
        
        return comment
        
    except Exception as e:
        logger.error(f"failed to generate weather comment: {e}")
        return None



