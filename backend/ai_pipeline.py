"""
AI Pipeline
Uses OpenAI to transform extracted content into structured itineraries
"""

import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


EXTRACTION_PROMPT = """You are a travel expert AI that converts social media travel content into detailed, actionable trip itineraries.

Given the following content from a travel video/post, extract and create a comprehensive travel itinerary.

CONTENT:
Platform: {platform}
Creator: {creator}
Title: {title}
Description: {description}
{transcript_section}

USER PREFERENCES:
Duration: {duration}
Style: {preferences}

YOUR TASK:
1. Identify the destination(s) mentioned
2. Extract ALL specific places mentioned (restaurants, attractions, hotels, activities)
3. Organize them into a logical day-by-day itinerary
4. Add helpful context and tips based on your knowledge
5. Fill in gaps with relevant recommendations that match the vibe of the original content

IMPORTANT GUIDELINES:
- Be specific with location names and addresses when possible
- Include a mix of the creator's recommendations AND your own relevant additions
- Provide practical tips (best times to visit, what to order, how to get there)
- Match the energy/vibe of the original content (if it's budget travel, keep it budget-friendly)
- If the content mentions a specific neighborhood or area, include other nearby gems
- Include local phrases if relevant to the destination
- Add packing tips specific to the destination

Respond in the following JSON format:
{{
    "destination": "City, Country",
    "duration_days": <number>,
    "summary": "2-3 sentence overview of the trip",
    "vibe": "Short description like 'Adventure & Culture' or 'Foodie Paradise'",
    "best_time_to_visit": "Season or months",
    "estimated_budget": "Budget range per day",
    "days": [
        {{
            "day": 1,
            "title": "Catchy title for the day",
            "locations": [
                {{
                    "name": "Place name",
                    "type": "restaurant|attraction|hotel|activity|neighborhood",
                    "description": "What it is and why it's special",
                    "address": "Address if known",
                    "price_level": "$|$$|$$$|$$$$",
                    "tips": "Insider tip"
                }}
            ],
            "notes": "Optional day-level notes"
        }}
    ],
    "packing_tips": ["tip1", "tip2"],
    "local_phrases": [
        {{"phrase": "local phrase", "meaning": "English meaning"}}
    ]
}}

Ensure your response is valid JSON only, no additional text."""


async def generate_itinerary(
    content_data: Dict[str, Any],
    source_url: str,
    duration_override: Optional[int] = None,
    preferences: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use GPT-4 to generate a structured itinerary from extracted content
    """

    # Build transcript section
    transcript_section = ""
    if content_data.get('transcript'):
        transcript_section = f"Transcript/Captions:\n{content_data['transcript']}"

    # Build duration instruction
    duration_instruction = "Infer appropriate duration from content (typically 3-7 days)"
    if duration_override:
        duration_instruction = f"Create a {duration_override}-day itinerary"

    # Build preferences instruction
    preferences_instruction = "Match the style/vibe of the original content"
    if preferences:
        preferences_instruction = f"Style preferences: {preferences}"

    prompt = EXTRACTION_PROMPT.format(
        platform=content_data.get('platform', 'unknown'),
        creator=content_data.get('creator', 'unknown'),
        title=content_data.get('title', ''),
        description=content_data.get('description', ''),
        transcript_section=transcript_section,
        duration=duration_instruction,
        preferences=preferences_instruction
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a travel expert that creates detailed, actionable travel itineraries. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Add source information
        result['source_url'] = source_url
        result['source_creator'] = content_data.get('creator', '')

        # Ensure required fields exist
        if 'days' not in result:
            result['days'] = []
        if 'duration_days' not in result:
            result['duration_days'] = len(result['days'])
        if 'packing_tips' not in result:
            result['packing_tips'] = []
        if 'local_phrases' not in result:
            result['local_phrases'] = []

        return result

    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract JSON from response
        raw_content = response.choices[0].message.content
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_content)
        if json_match:
            result = json.loads(json_match.group())
            result['source_url'] = source_url
            result['source_creator'] = content_data.get('creator', '')
            return result
        raise ValueError(f"Failed to parse AI response as JSON: {e}")

    except Exception as e:
        raise ValueError(f"AI generation failed: {str(e)}")


async def enhance_location(location: Dict[str, Any], destination: str) -> Dict[str, Any]:
    """
    Use AI to enhance a single location with more details
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a local travel expert. Enhance location information with practical details."
                },
                {
                    "role": "user",
                    "content": f"""Enhance this location in {destination}:
                    Name: {location.get('name')}
                    Type: {location.get('type')}
                    Current description: {location.get('description', '')}

                    Add: specific address (if you know it), best time to visit, insider tips, what to order/do.

                    Respond in JSON: {{"address": "", "tips": "", "best_time": "", "must_try": ""}}"""
                }
            ],
            temperature=0.5,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        enhancements = json.loads(response.choices[0].message.content)
        location.update({k: v for k, v in enhancements.items() if v})
        return location

    except:
        return location


async def generate_summary_from_itinerary(itinerary: Dict[str, Any]) -> str:
    """
    Generate a shareable summary of the itinerary
    """
    try:
        days_summary = []
        for day in itinerary.get('days', []):
            locations = [loc['name'] for loc in day.get('locations', [])]
            days_summary.append(f"Day {day['day']}: {', '.join(locations)}")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""Create a catchy, shareable 2-sentence summary for this trip:
                    Destination: {itinerary.get('destination')}
                    Duration: {itinerary.get('duration_days')} days
                    Vibe: {itinerary.get('vibe')}
                    Highlights: {'; '.join(days_summary[:3])}

                    Make it exciting and Instagram-worthy!"""
                }
            ],
            temperature=0.8,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()

    except:
        return itinerary.get('summary', '')
