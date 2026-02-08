"""
TikTok-to-Trip API
Converts social media travel content into structured, actionable itineraries
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import os
from dotenv import load_dotenv

from content_extractor import extract_content_from_url
from ai_pipeline import generate_itinerary
from places_enrichment import enrich_locations

load_dotenv()

app = FastAPI(
    title="TikTok-to-Trip API",
    description="Transform travel inspiration from social media into actionable trip itineraries",
    version="0.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Models ============

class TripRequest(BaseModel):
    url: str
    trip_duration: Optional[int] = None  # Days, if user wants to extend/compress
    preferences: Optional[str] = None  # e.g., "budget-friendly", "luxury", "foodie"


class Location(BaseModel):
    name: str
    type: str  # restaurant, attraction, hotel, activity
    description: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[dict] = None  # {lat, lng}
    rating: Optional[float] = None
    price_level: Optional[str] = None
    image_url: Optional[str] = None
    booking_url: Optional[str] = None
    tips: Optional[str] = None


class DayPlan(BaseModel):
    day: int
    title: str
    locations: List[Location]
    notes: Optional[str] = None


class Itinerary(BaseModel):
    destination: str
    duration_days: int
    summary: str
    vibe: str  # e.g., "Adventure & Culture", "Relaxed Beach Escape"
    best_time_to_visit: Optional[str] = None
    estimated_budget: Optional[str] = None
    days: List[DayPlan]
    source_url: str
    source_creator: Optional[str] = None
    packing_tips: Optional[List[str]] = None
    local_phrases: Optional[List[dict]] = None  # [{phrase, meaning}]


class ProcessingStatus(BaseModel):
    status: str
    message: str
    progress: int  # 0-100


# ============ Endpoints ============

@app.get("/")
async def root():
    return {
        "name": "TikTok-to-Trip API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "POST /api/extract": "Extract itinerary from social media URL",
            "GET /api/health": "Health check"
        }
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/api/extract", response_model=Itinerary)
async def extract_itinerary(request: TripRequest):
    """
    Main endpoint: Takes a TikTok/Instagram URL and returns a structured itinerary
    """

    # Validate URL
    if not any(domain in request.url.lower() for domain in ['tiktok.com', 'instagram.com', 'youtube.com', 'vm.tiktok.com']):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid TikTok, Instagram, or YouTube URL"
        )

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )

    try:
        # Step 1: Extract content from URL (video transcript, captions, description)
        content_data = await extract_content_from_url(request.url)

        if not content_data:
            raise HTTPException(
                status_code=422,
                detail="Could not extract content from this URL. The video might be private or unavailable."
            )

        # Step 2: Use AI to generate structured itinerary
        itinerary = await generate_itinerary(
            content_data=content_data,
            source_url=request.url,
            duration_override=request.trip_duration,
            preferences=request.preferences
        )

        # Step 3: Enrich with Google Places data (if API key available)
        if os.getenv("GOOGLE_PLACES_API_KEY"):
            itinerary = await enrich_locations(itinerary)

        return itinerary

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing content: {str(e)}"
        )


@app.post("/api/extract/demo")
async def extract_itinerary_demo():
    """
    Demo endpoint that returns a sample itinerary without requiring a real URL
    Useful for testing the frontend
    """
    return Itinerary(
        destination="Tokyo, Japan",
        duration_days=5,
        summary="An incredible 5-day journey through Tokyo, blending ancient temples with cutting-edge technology, world-class cuisine, and hidden local gems.",
        vibe="Culture & Culinary Adventure",
        best_time_to_visit="March-May (cherry blossoms) or October-November (autumn colors)",
        estimated_budget="$150-200/day (mid-range)",
        source_url="https://tiktok.com/@traveler/video/demo",
        source_creator="@tokyofoodie",
        days=[
            DayPlan(
                day=1,
                title="Shibuya & Harajuku - Modern Tokyo",
                locations=[
                    Location(
                        name="Shibuya Crossing",
                        type="attraction",
                        description="The world's busiest pedestrian crossing - an iconic Tokyo experience",
                        address="Shibuya, Tokyo",
                        tips="Best viewed from Starbucks above or Shibuya Sky observation deck"
                    ),
                    Location(
                        name="Ichiran Ramen Shibuya",
                        type="restaurant",
                        description="Famous solo-dining ramen experience with customizable noodles",
                        address="1-22-7 Jinnan, Shibuya",
                        price_level="$$",
                        tips="Go during off-peak hours (2-5pm) to avoid the queue"
                    ),
                    Location(
                        name="Takeshita Street",
                        type="attraction",
                        description="Harajuku's famous pedestrian street full of quirky fashion and crepes",
                        address="Harajuku, Shibuya"
                    ),
                    Location(
                        name="Meiji Shrine",
                        type="attraction",
                        description="Serene Shinto shrine surrounded by forest - perfect contrast to busy Harajuku",
                        address="1-1 Yoyogikamizonocho, Shibuya"
                    )
                ],
                notes="Start early at Meiji Shrine before the crowds, then explore Harajuku and Shibuya"
            ),
            DayPlan(
                day=2,
                title="Asakusa & Akihabara - Old Meets New",
                locations=[
                    Location(
                        name="Senso-ji Temple",
                        type="attraction",
                        description="Tokyo's oldest temple with the iconic Kaminarimon gate",
                        address="2-3-1 Asakusa, Taito",
                        tips="Arrive before 9am for photos without crowds"
                    ),
                    Location(
                        name="Nakamise Shopping Street",
                        type="attraction",
                        description="Traditional shopping street leading to Senso-ji",
                        tips="Try the fresh melon pan and ningyo-yaki (small cakes)"
                    ),
                    Location(
                        name="Akihabara Electric Town",
                        type="attraction",
                        description="Electronics, anime, and gaming paradise",
                        address="Akihabara, Chiyoda"
                    ),
                    Location(
                        name="Kanda Matsuya",
                        type="restaurant",
                        description="100-year-old soba noodle shop - local favorite",
                        address="1-13 Kanda Sudacho, Chiyoda",
                        price_level="$"
                    )
                ],
                notes="Take the Sumida River water bus from Asakusa to see Tokyo from the water"
            ),
            DayPlan(
                day=3,
                title="Tsukiji & Ginza - Food & Luxury",
                locations=[
                    Location(
                        name="Tsukiji Outer Market",
                        type="attraction",
                        description="Food lover's paradise - fresh sushi, tamagoyaki, and street food",
                        address="Tsukiji, Chuo",
                        tips="Must try: fresh sushi breakfast, tamagoyaki, and strawberry daifuku"
                    ),
                    Location(
                        name="Sushi Dai",
                        type="restaurant",
                        description="Legendary omakase experience - worth the wait",
                        price_level="$$$",
                        tips="Queue starts at 5am, expect 2-3 hour wait"
                    ),
                    Location(
                        name="Ginza District",
                        type="attraction",
                        description="Upscale shopping and dining district",
                        address="Ginza, Chuo"
                    ),
                    Location(
                        name="teamLab Borderless",
                        type="attraction",
                        description="Immersive digital art museum - absolutely stunning",
                        address="Azabudai Hills, Minato",
                        tips="Book tickets in advance, wear white clothes for better photos"
                    )
                ],
                notes="Combine morning market visit with afternoon Ginza exploration"
            ),
            DayPlan(
                day=4,
                title="Day Trip - Nikko or Kamakura",
                locations=[
                    Location(
                        name="Nikko Toshogu Shrine",
                        type="attraction",
                        description="UNESCO World Heritage site with ornate carvings and mountain scenery",
                        address="Nikko, Tochigi Prefecture",
                        tips="Get the Nikko Pass for discounted transport and entry"
                    ),
                    Location(
                        name="Shinkyo Bridge",
                        type="attraction",
                        description="Sacred vermillion bridge over the Daiya River"
                    ),
                    Location(
                        name="Yuba (Tofu Skin) Lunch",
                        type="restaurant",
                        description="Nikko specialty - silky tofu skin in various preparations",
                        price_level="$$"
                    )
                ],
                notes="Alternative: Visit Kamakura for the Great Buddha and beach vibes. Both are ~2 hours from Tokyo."
            ),
            DayPlan(
                day=5,
                title="Shinjuku & Departure",
                locations=[
                    Location(
                        name="Shinjuku Gyoen",
                        type="attraction",
                        description="Beautiful garden perfect for a peaceful morning",
                        address="11 Naitomachi, Shinjuku",
                        tips="Best during cherry blossom or autumn season"
                    ),
                    Location(
                        name="Omoide Yokocho (Memory Lane)",
                        type="attraction",
                        description="Atmospheric alley of tiny yakitori bars - old Tokyo vibes",
                        address="Nishi-Shinjuku, Shinjuku",
                        tips="Best experienced in the evening, but worth walking through anytime"
                    ),
                    Location(
                        name="Don Quijote Shinjuku",
                        type="attraction",
                        description="Massive discount store for last-minute souvenirs",
                        address="1-16-5 Kabukicho, Shinjuku",
                        tips="Open 24 hours - tax-free shopping for tourists"
                    )
                ],
                notes="Leave time for last-minute shopping and getting to the airport"
            )
        ],
        packing_tips=[
            "Comfortable walking shoes - you'll walk 15-20k steps daily",
            "Portable WiFi or SIM card - essential for navigation",
            "Small towel - many restrooms don't have hand dryers",
            "Cash - many small restaurants are cash-only",
            "Layers - weather can be unpredictable"
        ],
        local_phrases=[
            {"phrase": "Sumimasen", "meaning": "Excuse me / Sorry"},
            {"phrase": "Oishii", "meaning": "Delicious"},
            {"phrase": "Ikura desu ka?", "meaning": "How much is this?"},
            {"phrase": "Kanpai!", "meaning": "Cheers!"},
            {"phrase": "Arigatou gozaimasu", "meaning": "Thank you very much"}
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
