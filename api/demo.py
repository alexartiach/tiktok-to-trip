"""
Vercel Serverless Function - Demo Itinerary
Returns a sample Tokyo itinerary for testing
"""

from http.server import BaseHTTPRequestHandler
import json


DEMO_ITINERARY = {
    "destination": "Tokyo, Japan",
    "duration_days": 5,
    "summary": "An incredible 5-day journey through Tokyo, blending ancient temples with cutting-edge technology, world-class cuisine, and hidden local gems.",
    "vibe": "Culture & Culinary Adventure",
    "best_time_to_visit": "March-May (cherry blossoms) or October-November (autumn colors)",
    "estimated_budget": "$150-200/day (mid-range)",
    "source_url": "https://tiktok.com/@traveler/video/demo",
    "source_creator": "@tokyofoodie",
    "days": [
        {
            "day": 1,
            "title": "Shibuya & Harajuku - Modern Tokyo",
            "locations": [
                {
                    "name": "Shibuya Crossing",
                    "type": "attraction",
                    "description": "The world's busiest pedestrian crossing - an iconic Tokyo experience",
                    "address": "Shibuya, Tokyo",
                    "tips": "Best viewed from Starbucks above or Shibuya Sky observation deck"
                },
                {
                    "name": "Ichiran Ramen Shibuya",
                    "type": "restaurant",
                    "description": "Famous solo-dining ramen experience with customizable noodles",
                    "address": "1-22-7 Jinnan, Shibuya",
                    "price_level": "$$",
                    "tips": "Go during off-peak hours (2-5pm) to avoid the queue"
                },
                {
                    "name": "Takeshita Street",
                    "type": "attraction",
                    "description": "Harajuku's famous pedestrian street full of quirky fashion and crepes"
                },
                {
                    "name": "Meiji Shrine",
                    "type": "attraction",
                    "description": "Serene Shinto shrine surrounded by forest - perfect contrast to busy Harajuku",
                    "address": "1-1 Yoyogikamizonocho, Shibuya"
                }
            ],
            "notes": "Start early at Meiji Shrine before the crowds, then explore Harajuku and Shibuya"
        },
        {
            "day": 2,
            "title": "Asakusa & Akihabara - Old Meets New",
            "locations": [
                {
                    "name": "Senso-ji Temple",
                    "type": "attraction",
                    "description": "Tokyo's oldest temple with the iconic Kaminarimon gate",
                    "address": "2-3-1 Asakusa, Taito",
                    "tips": "Arrive before 9am for photos without crowds"
                },
                {
                    "name": "Nakamise Shopping Street",
                    "type": "attraction",
                    "description": "Traditional shopping street leading to Senso-ji",
                    "tips": "Try the fresh melon pan and ningyo-yaki"
                },
                {
                    "name": "Akihabara Electric Town",
                    "type": "attraction",
                    "description": "Electronics, anime, and gaming paradise",
                    "address": "Akihabara, Chiyoda"
                },
                {
                    "name": "Kanda Matsuya",
                    "type": "restaurant",
                    "description": "100-year-old soba noodle shop - local favorite",
                    "address": "1-13 Kanda Sudacho, Chiyoda",
                    "price_level": "$"
                }
            ],
            "notes": "Take the Sumida River water bus from Asakusa"
        },
        {
            "day": 3,
            "title": "Tsukiji & Ginza - Food & Luxury",
            "locations": [
                {
                    "name": "Tsukiji Outer Market",
                    "type": "attraction",
                    "description": "Food lover's paradise - fresh sushi, tamagoyaki, and street food",
                    "tips": "Must try: fresh sushi breakfast, tamagoyaki, strawberry daifuku"
                },
                {
                    "name": "Sushi Dai",
                    "type": "restaurant",
                    "description": "Legendary omakase experience",
                    "price_level": "$$$",
                    "tips": "Queue starts at 5am, expect 2-3 hour wait"
                },
                {
                    "name": "Ginza District",
                    "type": "attraction",
                    "description": "Upscale shopping and dining district"
                },
                {
                    "name": "teamLab Borderless",
                    "type": "attraction",
                    "description": "Immersive digital art museum - absolutely stunning",
                    "address": "Azabudai Hills, Minato",
                    "tips": "Book tickets in advance, wear white for better photos"
                }
            ],
            "notes": "Morning market + afternoon Ginza exploration"
        },
        {
            "day": 4,
            "title": "Day Trip - Nikko",
            "locations": [
                {
                    "name": "Nikko Toshogu Shrine",
                    "type": "attraction",
                    "description": "UNESCO World Heritage site with ornate carvings",
                    "tips": "Get the Nikko Pass for discounted transport"
                },
                {
                    "name": "Shinkyo Bridge",
                    "type": "attraction",
                    "description": "Sacred vermillion bridge over the Daiya River"
                },
                {
                    "name": "Yuba Lunch",
                    "type": "restaurant",
                    "description": "Nikko specialty - silky tofu skin dishes",
                    "price_level": "$$"
                }
            ],
            "notes": "Alternative: Visit Kamakura for the Great Buddha"
        },
        {
            "day": 5,
            "title": "Shinjuku & Departure",
            "locations": [
                {
                    "name": "Shinjuku Gyoen",
                    "type": "attraction",
                    "description": "Beautiful garden perfect for a peaceful morning",
                    "address": "11 Naitomachi, Shinjuku"
                },
                {
                    "name": "Omoide Yokocho",
                    "type": "attraction",
                    "description": "Atmospheric alley of tiny yakitori bars",
                    "tips": "Best in the evening but worth walking through anytime"
                },
                {
                    "name": "Don Quijote Shinjuku",
                    "type": "attraction",
                    "description": "Massive discount store for souvenirs",
                    "tips": "Open 24 hours - tax-free for tourists"
                }
            ],
            "notes": "Leave time for last-minute shopping"
        }
    ],
    "packing_tips": [
        "Comfortable walking shoes - you'll walk 15-20k steps daily",
        "Portable WiFi or SIM card - essential for navigation",
        "Small towel - many restrooms don't have hand dryers",
        "Cash - many small restaurants are cash-only",
        "Layers - weather can be unpredictable"
    ],
    "local_phrases": [
        {"phrase": "Sumimasen", "meaning": "Excuse me / Sorry"},
        {"phrase": "Oishii", "meaning": "Delicious"},
        {"phrase": "Ikura desu ka?", "meaning": "How much is this?"},
        {"phrase": "Kanpai!", "meaning": "Cheers!"},
        {"phrase": "Arigatou gozaimasu", "meaning": "Thank you very much"}
    ]
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(DEMO_ITINERARY).encode())

    def do_GET(self):
        self.do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
