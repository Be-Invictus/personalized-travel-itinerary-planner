"""
Configuration, Constants, and Reference Data for Travel Planner.
"""

from typing import Dict, Any, List

APP_TITLE = "Personalized Travel Itinerary Planner"
APP_SUBTITLE = "Smart AI-powered journey curation with geographic clustering & dynamic day-crafting"
VERSION = "2.4.0"

# Supported LLM Providers & Models
PROVIDERS = {
    "Gemini": {
        "name": "Google Gemini",
        "models": ["gemini-2.5-flash", "gemini-1.5-flash"],
        "default_model": "gemini-2.5-flash",
        "key_env": "GEMINI_API_KEY",
        "key_label": "Enter Gemini API Key"
    },
    "Groq": {
        "name": "Groq Cloud",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        "default_model": "llama-3.3-70b-versatile",
        "key_env": "GROQ_API_KEY",
        "key_label": "Enter Groq API Key"
    }
}

# Currency Conversion Rates (Base USD)
CURRENCIES = {
    "USD": {"symbol": "$", "rate_from_usd": 1.0, "name": "US Dollar"},
    "EUR": {"symbol": "€", "rate_from_usd": 0.92, "name": "Euro"},
    "GBP": {"symbol": "£", "rate_from_usd": 0.79, "name": "British Pound"},
    "JPY": {"symbol": "¥", "rate_from_usd": 155.0, "name": "Japanese Yen"},
    "INR": {"symbol": "₹", "rate_from_usd": 86.5, "name": "Indian Rupee"},
    "AUD": {"symbol": "A$", "rate_from_usd": 1.54, "name": "Australian Dollar"},
    "CAD": {"symbol": "C$", "rate_from_usd": 1.40, "name": "Canadian Dollar"},
    "SGD": {"symbol": "S$", "rate_from_usd": 1.34, "name": "Singapore Dollar"},
    "THB": {"symbol": "฿", "rate_from_usd": 34.5, "name": "Thai Baht"},
    "AED": {"symbol": "AED ", "rate_from_usd": 3.67, "name": "UAE Dirham"},
    "CHF": {"symbol": "CHF ", "rate_from_usd": 0.89, "name": "Swiss Franc"},
    "IDR": {"symbol": "Rp ", "rate_from_usd": 16200.0, "name": "Indonesian Rupiah"},
}

# Benchmark Daily Budget Ranges (USD per person)
BUDGET_TIERS = {
    "Budget": {"min_usd": 40, "max_usd": 85, "desc": "Hostels/guesthouses, public transit, street food & free landmarks"},
    "Moderate": {"min_usd": 100, "max_usd": 220, "desc": "Boutique hotels, casual dining, rideshare/metro, guided museums"},
    "Luxury": {"min_usd": 300, "max_usd": 800, "desc": "5-star resorts, fine dining, private transfers, exclusive access"}
}

TRAVEL_PARTY_OPTIONS = [
    "Solo Traveler",
    "Couple / Romantic",
    "Family with Kids",
    "Group of Friends",
    "Business & Leisure (Bleisure)"
]

PACE_OPTIONS = [
    "Relaxed (2 activities/day + ample downtime)",
    "Moderate (3-4 activities with balanced breaks)",
    "Fast-Paced (Packed highlights from dawn to late night)"
]

INTEREST_OPTIONS = [
    "Food & Culinary Trails",
    "Art, History & Museums",
    "Nature & Scenic Landscapes",
    "Outdoor Adventure & Hiking",
    "Nightlife, Bars & Music",
    "Relaxation, Spas & Wellness",
    "Architecture & Urban Vibe",
    "Local Markets & Shopping",
    "Photography & Instagram Hotspots"
]

VIBE_CATEGORIES = [
    "Beach & Coastal Sun",
    "Mountains, Hiking & Serenity",
    "Historic & Cultural Heritage",
    "Vibrant Urban Megacity",
    "Romantic & Scenic Escapes",
    "Off-the-Beaten-Path Nature",
    "Foodie Paradise & Wine Tasting"
]

# Destination Quick Directory (Meta-info for smart defaults & demo clustering)
DESTINATION_METADATA = {
    "Kyoto, Japan": {
        "currency": "JPY",
        "symbol": "¥",
        "country": "Japan",
        "police": "110",
        "ambulance": "119",
        "hospital": "Kyoto University Hospital International Clinic",
        "clusters": ["Higashiyama & Gion", "Arashiyama & Sagano", "Kinkaku-ji & Northern Hills", "Central Kyoto & Fushimi Inari"],
        "cultural_tips": ["Remove shoes when entering temples & traditional ryokans.", "Keep voice low on buses and subways.", "No tipping needed in restaurants."]
    },
    "Paris, France": {
        "currency": "EUR",
        "symbol": "€",
        "country": "France",
        "police": "17",
        "ambulance": "15",
        "hospital": "American Hospital of Paris (Neuilly)",
        "clusters": ["Le Marais & Île de la Cité", "Montmartre & 18th Arr.", "Latin Quarter & Saint-Germain", "Eiffel Tower & Champs-Élysées"],
        "cultural_tips": ["Always greet shopkeepers with 'Bonjour' upon entering.", "Validate metro tickets before boarding.", "Keep bags secure around tourist hubs."]
    },
    "Bali, Indonesia": {
        "currency": "IDR",
        "symbol": "Rp ",
        "country": "Indonesia",
        "police": "110",
        "ambulance": "118",
        "hospital": "BIMC Hospital Kuta / Ubud",
        "clusters": ["Ubud Cultural Heart", "Seminyak & Canggu Coast", "Uluwatu Cliffs & South Coast", "Nusa Penida & Sanur"],
        "cultural_tips": ["Wear a sarong and sash when visiting sacred temples.", "Drink bottled or filtered water only.", "Respect daily Canang Sari street offerings."]
    },
    "Barcelona, Spain": {
        "currency": "EUR",
        "symbol": "€",
        "country": "Spain",
        "police": "112",
        "ambulance": "112",
        "hospital": "Hospital Clínic de Barcelona",
        "clusters": ["Gothic Quarter & Born", "Eixample & Gaudí Architecture", "Gràcia & Park Güell", "Barceloneta & Olympic Port"],
        "cultural_tips": ["Dinner typically starts after 8:30 PM.", "Watch personal belongings on Las Ramblas.", "Pre-book Sagrada Família tickets weeks ahead."]
    },
    "Amalfi Coast, Italy": {
        "currency": "EUR",
        "symbol": "€",
        "country": "Italy",
        "police": "113",
        "ambulance": "118",
        "hospital": "Castiglione di Ravello Hospital",
        "clusters": ["Positano Cliffside & Marina", "Amalfi Town & Cathedral Square", "Ravello Gardens & Heights", "Capri Island Excursion"],
        "cultural_tips": ["Wear comfortable walking shoes with grip for steep staircases.", "Ferries are faster than coastal buses in peak season.", "Order espresso at the counter for local price."]
    },
    "Jaipur & Rajasthan, India": {
        "currency": "INR",
        "symbol": "₹",
        "country": "India",
        "police": "112",
        "ambulance": "102",
        "hospital": "Fortis Escorts Hospital Jaipur",
        "clusters": ["Old Walled Pink City", "Amer & Jaigarh Fort Ridge", "Civil Lines & Royal Palaces", "C-Scheme Cafes & Bazaars"],
        "cultural_tips": ["Remove footwear before entering shrines and heritage sanctums.", "Negotiate gently at open bazaars.", "Stay hydrated and drink filtered mineral water."]
    }
}
