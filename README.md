# TikTok-to-Trip

**Transform travel inspiration from social media into actionable trip itineraries.**

Paste a TikTok, Instagram, or YouTube travel video URL and get a detailed, day-by-day itinerary with locations, restaurants, tips, and more.

![Demo](https://via.placeholder.com/800x400/f97316/ffffff?text=TikTok+to+Trip+Demo)

## Features

- **Multi-Platform Support**: Works with TikTok, Instagram Reels, and YouTube
- **AI-Powered Extraction**: Automatically identifies locations, restaurants, and activities
- **Structured Itineraries**: Day-by-day plans with addresses and tips
- **Google Places Integration**: Verified location data, ratings, and photos
- **Customizable**: Adjust trip duration and travel style preferences

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- (Optional) Google Places API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit `http://localhost:3000` to use the app.

## API Endpoints

### `POST /api/extract`

Extract an itinerary from a social media URL.

**Request:**
```json
{
  "url": "https://www.tiktok.com/@user/video/123456",
  "trip_duration": 5,
  "preferences": "foodie"
}
```

**Response:**
```json
{
  "destination": "Tokyo, Japan",
  "duration_days": 5,
  "summary": "An incredible 5-day journey...",
  "vibe": "Culture & Culinary Adventure",
  "days": [
    {
      "day": 1,
      "title": "Shibuya & Harajuku",
      "locations": [...]
    }
  ],
  "packing_tips": [...],
  "local_phrases": [...]
}
```

### `POST /api/extract/demo`

Returns a sample Tokyo itinerary for testing without requiring API calls.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + Tailwind CSS                                        │
├─────────────────────────────────────────────────────────────┤
│                        BACKEND                               │
│  FastAPI                                                     │
│  ├── content_extractor.py (Video/content fetching)          │
│  ├── ai_pipeline.py (GPT-4 itinerary generation)           │
│  └── places_enrichment.py (Google Places data)             │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: Python, FastAPI, OpenAI GPT-4, yt-dlp
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **APIs**: OpenAI, Google Places (optional)

## Development

### Running Tests

```bash
cd backend
pytest
```

### Building for Production

```bash
cd frontend
npm run build
```

## Roadmap

- [ ] User accounts and saved itineraries
- [ ] Direct booking integration (flights, hotels)
- [ ] Social sharing features
- [ ] Mobile app (React Native)
- [ ] Chrome extension for one-click extraction
- [ ] Collaborative trip planning

## Acquisition Potential

This product addresses a clear gap in the market:

1. **Unique Technical Moat**: Extracting structured data from unstructured video content
2. **Meets Users Where They Are**: Gen Z already uses TikTok/Instagram for travel inspiration
3. **Multiple Acquirer Paths**:
   - Social platforms (TikTok, Meta) - adds commerce layer
   - OTAs (Booking.com, Expedia) - content-to-commerce
   - Fintech (Revolut) - fits their Swifty acquisition strategy

## License

MIT

## Contributing

Contributions welcome! Please read our contributing guidelines first.

---

Built with ❤️ by [Your Name]
