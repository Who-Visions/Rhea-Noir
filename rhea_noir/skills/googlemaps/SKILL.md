---
name: googlemaps
version: 1.0.0
description: Gemini Google Maps Grounding - Location-aware AI responses
---

# Google Maps Skill

Enable location-aware responses using Gemini + Google Maps data.

## Features

- **Accurate Location Data**: Leverage 250M+ places worldwide
- **Personalized Recommendations**: Based on user location
- **Itinerary Planning**: Multi-day trip planning
- **Citations**: Sources linked to Google Maps

## Capabilities

| Action | Description |
|--------|-------------|
| `search_places` | Find places near a location |
| `get_recommendations` | Get personalized suggestions |
| `plan_itinerary` | Create trip/day plans |
| `ask_about_place` | Ask questions about specific places |

## Usage Examples

### Find Nearby Places
```python
from rhea_noir.skills.googlemaps.actions import skill as gm

result = gm.search_places(
    query="best Italian restaurants",
    latitude=34.050481,
    longitude=-118.248526
)
```

### Get Recommendations
```python
result = gm.get_recommendations(
    query="family-friendly restaurants with playgrounds",
    latitude=30.2672,
    longitude=-97.7431
)
```

### Plan a Day Trip
```python
result = gm.plan_itinerary(
    query="Plan a day: Golden Gate Bridge, museum, nice dinner",
    latitude=37.78193,
    longitude=-122.40476
)
```

## Response Includes

- **Answer**: Natural language response
- **Sources**: Google Maps places with links
- **Place IDs**: For further API integration
- **Widget Token**: For rendering Maps widget

## Pricing

$25 per 1K grounded prompts (500 free/day).

> [!NOTE]
> Not available with Gemini 3 models. Use Gemini 2.5 Flash/Pro.
