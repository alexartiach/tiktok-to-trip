"""
Content Extractor
Fetches and extracts content from TikTok, Instagram, and YouTube URLs
"""

import httpx
import re
import json
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import subprocess
import tempfile
import os


async def extract_content_from_url(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract content from a social media URL
    Returns dict with: title, description, transcript, creator, platform
    """

    url_lower = url.lower()

    if 'tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower:
        return await extract_tiktok(url)
    elif 'instagram.com' in url_lower:
        return await extract_instagram(url)
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return await extract_youtube(url)
    else:
        return None


async def extract_tiktok(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract content from TikTok URL using yt-dlp
    """
    try:
        # Use yt-dlp to get video metadata
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # Fallback to web scraping
            return await extract_tiktok_fallback(url)

        data = json.loads(result.stdout)

        # Extract transcript/subtitles if available
        transcript = None
        if data.get('subtitles'):
            # Try to get English subtitles
            for lang in ['en', 'en-US', 'en-GB']:
                if lang in data['subtitles']:
                    transcript = await fetch_subtitles(data['subtitles'][lang])
                    break

        return {
            'platform': 'tiktok',
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'transcript': transcript,
            'creator': data.get('uploader', data.get('creator', '')),
            'creator_id': data.get('uploader_id', ''),
            'duration': data.get('duration', 0),
            'view_count': data.get('view_count', 0),
            'like_count': data.get('like_count', 0),
            'tags': data.get('tags', []),
            'thumbnail': data.get('thumbnail', ''),
        }

    except subprocess.TimeoutExpired:
        return await extract_tiktok_fallback(url)
    except Exception as e:
        print(f"TikTok extraction error: {e}")
        return await extract_tiktok_fallback(url)


async def extract_tiktok_fallback(url: str) -> Optional[Dict[str, Any]]:
    """
    Fallback TikTok extraction using web scraping
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
            }
            response = await client.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                return None

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find JSON-LD data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'VideoObject':
                        return {
                            'platform': 'tiktok',
                            'title': data.get('name', ''),
                            'description': data.get('description', ''),
                            'transcript': None,
                            'creator': data.get('creator', {}).get('name', ''),
                            'thumbnail': data.get('thumbnailUrl', ''),
                        }
                except:
                    continue

            # Fallback: extract from meta tags
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')

            title = ''
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title:
                title = og_title.get('content', '')

            return {
                'platform': 'tiktok',
                'title': title,
                'description': description,
                'transcript': None,
                'creator': extract_creator_from_url(url),
            }

    except Exception as e:
        print(f"TikTok fallback error: {e}")
        return None


async def extract_instagram(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract content from Instagram URL
    Note: Instagram is heavily protected, this is a best-effort extraction
    """
    try:
        # Try yt-dlp first
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'platform': 'instagram',
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'transcript': None,
                'creator': data.get('uploader', ''),
                'creator_id': data.get('uploader_id', ''),
            }

    except:
        pass

    # Fallback to basic scraping
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
            }
            response = await client.get(url, headers=headers, timeout=15)

            soup = BeautifulSoup(response.text, 'html.parser')

            description = ''
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc:
                description = meta_desc.get('content', '')

            title = ''
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title:
                title = og_title.get('content', '')

            return {
                'platform': 'instagram',
                'title': title,
                'description': description,
                'transcript': None,
                'creator': extract_creator_from_url(url),
            }
    except Exception as e:
        print(f"Instagram extraction error: {e}")
        return None


async def extract_youtube(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract content from YouTube URL
    YouTube has better subtitle support
    """
    try:
        # Get metadata
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)

        # Try to get transcript
        transcript = None
        if data.get('subtitles') or data.get('automatic_captions'):
            subs = data.get('subtitles', {}) or data.get('automatic_captions', {})
            for lang in ['en', 'en-US', 'en-GB', 'a.en']:
                if lang in subs:
                    transcript = await fetch_subtitles(subs[lang])
                    break

        return {
            'platform': 'youtube',
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'transcript': transcript,
            'creator': data.get('uploader', data.get('channel', '')),
            'creator_id': data.get('uploader_id', data.get('channel_id', '')),
            'duration': data.get('duration', 0),
            'view_count': data.get('view_count', 0),
            'like_count': data.get('like_count', 0),
            'tags': data.get('tags', []),
            'thumbnail': data.get('thumbnail', ''),
        }

    except Exception as e:
        print(f"YouTube extraction error: {e}")
        return None


async def fetch_subtitles(subtitle_info: list) -> Optional[str]:
    """
    Fetch and parse subtitles from subtitle URL
    """
    try:
        # Find a text-based format
        for sub in subtitle_info:
            if sub.get('ext') in ['vtt', 'srt', 'txt', 'json3']:
                async with httpx.AsyncClient() as client:
                    response = await client.get(sub['url'], timeout=10)
                    if response.status_code == 200:
                        return clean_subtitles(response.text, sub.get('ext', 'vtt'))
        return None
    except:
        return None


def clean_subtitles(content: str, format: str) -> str:
    """
    Clean subtitle content to plain text
    """
    # Remove VTT/SRT formatting
    lines = content.split('\n')
    text_lines = []

    for line in lines:
        line = line.strip()
        # Skip timing lines and headers
        if not line:
            continue
        if '-->' in line:
            continue
        if line.startswith('WEBVTT'):
            continue
        if line.isdigit():
            continue
        if re.match(r'^\d{2}:\d{2}', line):
            continue

        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)
        # Remove common VTT formatting
        line = re.sub(r'&nbsp;', ' ', line)

        if line:
            text_lines.append(line)

    return ' '.join(text_lines)


def extract_creator_from_url(url: str) -> str:
    """
    Extract creator username from URL
    """
    patterns = [
        r'tiktok\.com/@([^/\?]+)',
        r'instagram\.com/([^/\?]+)',
        r'youtube\.com/@([^/\?]+)',
        r'youtube\.com/channel/([^/\?]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"@{match.group(1)}"

    return ''
