"""
Places Enrichment
Enhances location data with Google Places API information
"""

import os
import httpx
from typing import Dict, Any, Optional, List

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"


async def enrich_locations(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich all locations in the itinerary with Google Places data
    """
    if not GOOGLE_PLACES_API_KEY:
        return itinerary

    destination = itinerary.get('destination', '')

    for day in itinerary.get('days', []):
        enriched_locations = []
        for location in day.get('locations', []):
            enriched = await enrich_single_location(location, destination)
            enriched_locations.append(enriched)
        day['locations'] = enriched_locations

    return itinerary


async def enrich_single_location(location: Dict[str, Any], destination: str) -> Dict[str, Any]:
    """
    Enrich a single location with Google Places data
    """
    if not GOOGLE_PLACES_API_KEY:
        return location

    try:
        # Search for the place
        place_data = await search_place(
            query=f"{location.get('name')} {destination}",
            location_type=location.get('type')
        )

        if place_data:
            # Get detailed information
            details = await get_place_details(place_data.get('place_id'))

            if details:
                # Update location with verified data
                location['address'] = details.get('formatted_address', location.get('address'))
                location['coordinates'] = {
                    'lat': details.get('geometry', {}).get('location', {}).get('lat'),
                    'lng': details.get('geometry', {}).get('location', {}).get('lng')
                }
                location['rating'] = details.get('rating')
                location['price_level'] = convert_price_level(details.get('price_level'))
                location['google_maps_url'] = details.get('url')

                # Get a photo if available
                if details.get('photos'):
                    photo_ref = details['photos'][0].get('photo_reference')
                    if photo_ref:
                        location['image_url'] = get_photo_url(photo_ref)

                # Get opening hours
                if details.get('opening_hours'):
                    location['opening_hours'] = details['opening_hours'].get('weekday_text', [])

        return location

    except Exception as e:
        print(f"Error enriching location {location.get('name')}: {e}")
        return location


async def search_place(query: str, location_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Search for a place using Google Places Text Search
    """
    if not GOOGLE_PLACES_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            params = {
                'query': query,
                'key': GOOGLE_PLACES_API_KEY
            }

            # Add type filtering if available
            type_mapping = {
                'restaurant': 'restaurant',
                'attraction': 'tourist_attraction',
                'hotel': 'lodging',
                'activity': 'point_of_interest',
                'neighborhood': 'neighborhood'
            }
            if location_type and location_type in type_mapping:
                params['type'] = type_mapping[location_type]

            response = await client.get(
                f"{PLACES_BASE_URL}/textsearch/json",
                params=params,
                timeout=10
            )

            data = response.json()

            if data.get('status') == 'OK' and data.get('results'):
                return data['results'][0]

            return None

    except Exception as e:
        print(f"Places search error: {e}")
        return None


async def get_place_details(place_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a place
    """
    if not GOOGLE_PLACES_API_KEY or not place_id:
        return None

    try:
        async with httpx.AsyncClient() as client:
            params = {
                'place_id': place_id,
                'key': GOOGLE_PLACES_API_KEY,
                'fields': 'name,formatted_address,geometry,rating,price_level,photos,opening_hours,url,website,formatted_phone_number,reviews'
            }

            response = await client.get(
                f"{PLACES_BASE_URL}/details/json",
                params=params,
                timeout=10
            )

            data = response.json()

            if data.get('status') == 'OK':
                return data.get('result')

            return None

    except Exception as e:
        print(f"Place details error: {e}")
        return None


def get_photo_url(photo_reference: str, max_width: int = 800) -> str:
    """
    Generate a Google Places photo URL
    """
    return f"{PLACES_BASE_URL}/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={GOOGLE_PLACES_API_KEY}"


def convert_price_level(google_price_level: Optional[int]) -> Optional[str]:
    """
    Convert Google's 0-4 price level to $ symbols
    """
    if google_price_level is None:
        return None

    mapping = {
        0: 'Free',
        1: '$',
        2: '$$',
        3: '$$$',
        4: '$$$$'
    }
    return mapping.get(google_price_level, None)


async def get_nearby_places(
    lat: float,
    lng: float,
    place_type: str = 'restaurant',
    radius: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get nearby places of a specific type
    Useful for suggesting alternatives or additions
    """
    if not GOOGLE_PLACES_API_KEY:
        return []

    try:
        async with httpx.AsyncClient() as client:
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': place_type,
                'key': GOOGLE_PLACES_API_KEY
            }

            response = await client.get(
                f"{PLACES_BASE_URL}/nearbysearch/json",
                params=params,
                timeout=10
            )

            data = response.json()

            if data.get('status') == 'OK':
                return data.get('results', [])[:5]  # Return top 5

            return []

    except Exception as e:
        print(f"Nearby search error: {e}")
        return []
