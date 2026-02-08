"""
Vercel Serverless Function - Extract Itinerary
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


EXTRACTION_PROMPT = """You are a travel expert AI that converts social media travel content into detailed, actionable trip itineraries.

Given the URL and any context, create a comprehensive travel itinerary for the destination that would likely be featured in this type of content.

URL: {url}
User Preferences:
- Duration: {duration}
- Style: {preferences}

YOUR TASK:
1. Identify the most likely destination from this URL/content
2. Create a realistic day-by-day itinerary
3. Include specific places (restaurants, attractions, activities)
4. Add helpful tips and local insights

Respond in this exact JSON format:
{{
    "destination": "City, Country",
    "duration_days": <number>,
    "summary": "2-3 sentence overview of the trip",
    "vibe": "Short description like 'Adventure & Culture' or 'Foodie Paradise'",
    "best_time_to_visit": "Season or months",
    "estimated_budget": "Budget range per day like '$100-150/day'",
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
    "packing_tips": ["tip1", "tip2", "tip3"],
    "local_phrases": [
        {{"phrase": "local phrase", "meaning": "English meaning"}}
    ]
}}

Return ONLY valid JSON, no other text."""


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            url = data.get('url', '')
            duration = data.get('trip_duration')
            preferences = data.get('preferences', '')

            # Validate URL
            valid_domains = ['tiktok.com', 'instagram.com', 'youtube.com', 'vm.tiktok.com', 'youtu.be']
            if not any(domain in url.lower() for domain in valid_domains):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "detail": "Please provide a valid TikTok, Instagram, or YouTube URL"
                }).encode())
                return

            # Check API key
            if not os.environ.get("OPENAI_API_KEY"):
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "detail": "OpenAI API key not configured"
                }).encode())
                return

            # Generate itinerary
            duration_text = f"{duration} days" if duration else "3-5 days (your choice)"
            pref_text = preferences if preferences else "balanced experience"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a travel expert. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": EXTRACTION_PROMPT.format(
                            url=url,
                            duration=duration_text,
                            preferences=pref_text
                        )
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result['source_url'] = url
            result['source_creator'] = self._extract_creator(url)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "detail": f"Error: {str(e)}"
            }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _extract_creator(self, url):
        import re
        patterns = [
            r'tiktok\.com/@([^/\?]+)',
            r'instagram\.com/([^/\?]+)',
            r'youtube\.com/@([^/\?]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"@{match.group(1)}"
        return None
