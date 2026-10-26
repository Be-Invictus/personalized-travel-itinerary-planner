"""
Configuration, Constants, and Reference Data for Travel Planner.
Extensive global destination knowledge base with geographic clusters, realistic currencies, and vibe matching.
"""

from typing import Dict, Any, List

APP_TITLE = "Personalized Travel Itinerary Planner"
APP_SUBTITLE = "Smart AI-powered journey curation with geographic clustering & dynamic day-crafting"
VERSION = "2.5.0"

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
    "NZD": {"symbol": "NZ$", "rate_from_usd": 1.68, "name": "New Zealand Dollar"},
    "MXN": {"symbol": "Mex$", "rate_from_usd": 20.2, "name": "Mexican Peso"},
    "EGP": {"symbol": "E£", "rate_from_usd": 49.5, "name": "Egyptian Pound"},
    "ZAR": {"symbol": "R ", "rate_from_usd": 18.2, "name": "South African Rand"},
    "ISK": {"symbol": "kr ", "rate_from_usd": 138.0, "name": "Icelandic Króna"},
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

# Comprehensive Destination Directory with Detailed Real Data
DESTINATION_CATALOG = [
    # 1. Mountains & Hiking
    {
        "city": "Interlaken & Swiss Alps",
        "country": "Switzerland",
        "vibes": ["Mountains, Hiking & Serenity", "Romantic & Scenic Escapes", "Off-the-Beaten-Path Nature"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Family with Kids", "Solo Traveler", "Group of Friends"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Relaxed (2 activities/day + ample downtime)"],
        "seasons": ["Summer (Jun - Aug)", "Winter (Dec - Feb)", "Spring (Mar - May)"],
        "currency": "CHF",
        "symbol": "CHF ",
        "daily_usd": 240.0,
        "tagline": "Turquoise alpine lakes cradled beneath the majestic Jungfrau and Eiger peaks.",
        "highlights": ["Jungfraujoch Top of Europe Cogwheel Train", "Lake Brienz Turquoise Steamboat Cruise", "Lauterbrunnen Valley of 72 Waterfalls", "Harder Kulm Panoramic Funicular Viewpoint"],
        "connectivity": "Direct trains from Zurich Airport (ZRH); Swiss Travel Pass integrated network",
        "why": "Unrivaled alpine majesty, safe scenic trains ideal for families and couples, and breathtaking Swiss hiking trails.",
        "clusters": ["Lauterbrunnen Valley & Waterfalls", "Grindelwald & First Cliff Walk", "Interlaken Lakes & Harder Kulm", "Mürren & Schilthorn Alpine Peak"],
        "cultural_tips": ["Train punctuality is world-class; board on time.", "Tap water from public fountains is pristine mineral water.", "Tipping is appreciated but rounded up."]
    },
    {
        "city": "Banff & Canadian Rockies",
        "country": "Canada",
        "vibes": ["Mountains, Hiking & Serenity", "Off-the-Beaten-Path Nature", "Outdoor Adventure & Hiking"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Family with Kids", "Group of Friends", "Couple / Romantic", "Solo Traveler"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Summer (Jun - Aug)", "Autumn / Fall (Sep - Nov)", "Winter (Dec - Feb)"],
        "currency": "CAD",
        "symbol": "C$",
        "daily_usd": 180.0,
        "tagline": "Glacial turquoise waters mirroring snow-capped Rocky Mountain peaks.",
        "highlights": ["Lake Louise & Moraine Lake Canoe Paddling", "Icefields Parkway Glacier Skywalk", "Banff Upper Hot Springs Soak", "Johnston Canyon Walkway Waterfall Trek"],
        "connectivity": "Fly into Calgary International (YYC), 90-minute scenic parkway drive",
        "why": "Unspoiled wilderness, pristine glacial lakes, and family-friendly wildlife sightings with superb trail safety.",
        "clusters": ["Banff Townsite & Sulphur Mountain", "Lake Louise & Moraine Lake", "Bow Valley Parkway & Johnston Canyon", "Canmore & Kananaskis Foothills"],
        "cultural_tips": ["Always maintain distance from elk and wildlife.", "Carry bear spray when hiking in backcountry.", "National Park pass required for entry."]
    },
    {
        "city": "Manali & Solang Valley",
        "country": "India",
        "vibes": ["Mountains, Hiking & Serenity", "Off-the-Beaten-Path Nature"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Group of Friends", "Couple / Romantic", "Solo Traveler", "Family with Kids"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Spring (Mar - May)", "Winter (Dec - Feb)", "Autumn / Fall (Sep - Nov)"],
        "currency": "INR",
        "symbol": "₹",
        "daily_usd": 65.0,
        "tagline": "Himalayan pine forests, gushing rivers, and snow-capped mountain passes.",
        "highlights": ["Solang Valley Paragliding & Skiing", "Rohtang Pass & Atal Tunnel Snow View", "Old Manali Artisan Cafes & Cedar Walks", "Jogini Waterfall Forest Trek"],
        "connectivity": "Flight to Bhuntar Airport (KUU) or scenic overnight luxury Volvo from Delhi/Chandigarh",
        "why": "Affordable mountain haven with riverside cafes, crisp Himalayan air, and high-altitude adventures.",
        "clusters": ["Old Manali Village & Manu Temple", "Solang Valley Adventure Bowl", "Naggar Castle & Heritage Art Gallery", "Vashisht Hot Springs & Jogi Falls"],
        "cultural_tips": ["Dress modestly when visiting ancient wooden temples.", "Bargain respectfully in Mall Road bazaars.", "Acclimatize before ascending high mountain passes."]
    },
    {
        "city": "Queenstown",
        "country": "New Zealand",
        "vibes": ["Mountains, Hiking & Serenity", "Off-the-Beaten-Path Nature"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Solo Traveler", "Group of Friends", "Couple / Romantic"],
        "paces": ["Fast-Paced (Packed highlights from dawn to late night)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Summer (Jun - Aug)", "Spring (Mar - May)", "Winter (Dec - Feb)"],
        "currency": "NZD",
        "symbol": "NZ$",
        "daily_usd": 210.0,
        "tagline": "The adventure capital of the Southern Hemisphere nestled beside Lake Wakatipu.",
        "highlights": ["Shotover River Jet Boat Thrill", "Milford Sound Fjord Helicopter & Cruise", "Skyline Gondola & Luge Track", "Central Otago Pinot Noir Winery Tour"],
        "connectivity": "Queenstown Airport (ZQN) with direct trans-Tasman flights",
        "why": "Adrenaline-fueled adventures combined with postcard-perfect South Island alpine scenery and craft dining.",
        "clusters": ["Queenstown Waterfront & Skyline Peak", "Arrowtown Historic Goldmining Valley", "Gibbston Valley Wine Trail", "Glenorchy & Dart River Valley"],
        "cultural_tips": ["Respect Tiaki Promise to care for New Zealand nature.", "Drive on the left side of the road.", "Book adventure excursions in advance."]
    },

    # 2. Beach & Coastal Sun
    {
        "city": "Amalfi Coast",
        "country": "Italy",
        "vibes": ["Beach & Coastal Sun", "Romantic & Scenic Escapes", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Group of Friends"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Summer (Jun - Aug)", "Spring (Mar - May)", "Autumn / Fall (Sep - Nov)"],
        "currency": "EUR",
        "symbol": "€",
        "daily_usd": 260.0,
        "tagline": "Cliffside pastel villages tumbling into azure Mediterranean waters.",
        "highlights": ["Positano Cliffside Terraces & Spiaggia Grande", "Ravello Villa Cimbrone Panoramic Gardens", "Path of the Gods Cliff Top Trail", "Private Capri Island & Blue Grotto Boat Charter"],
        "connectivity": "High-speed train to Salerno or Naples, followed by scenic coastal ferry",
        "why": "Unrivaled romance, iconic lemon groves, cliffside terrace dining, and stunning coastal ferry cruising.",
        "clusters": ["Positano Cliffside & Marina", "Amalfi Town & Cathedral Square", "Ravello Gardens & Heights", "Capri Island Excursion"],
        "cultural_tips": ["Ferries are vastly quicker than coastal buses.", "Espresso at the counter is the local tradition.", "Wear sturdy walking shoes for cliff steps."]
    },
    {
        "city": "Phuket & Phi Phi",
        "country": "Thailand",
        "vibes": ["Beach & Coastal Sun", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Solo Traveler", "Group of Friends", "Couple / Romantic", "Family with Kids"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Winter (Dec - Feb)", "Spring (Mar - May)", "Autumn / Fall (Sep - Nov)"],
        "currency": "THB",
        "symbol": "฿",
        "daily_usd": 70.0,
        "tagline": "Limestone karst cliffs, white sandy coves, and world-renowned night street food.",
        "highlights": ["Phi Phi Maya Bay Island Speedboat Tour", "Phang Nga Bay James Bond Island Kayak", "Old Phuket Town Sino-Portuguese Street Art & Night Market", "Promthep Cape Sunset Panorama"],
        "connectivity": "Phuket International Airport (HKT) with global direct charter flights",
        "why": "Exceptional affordability, vibrant nightlife for friends, tranquil beaches for couples, and world-class street food.",
        "clusters": ["Kata & Karon Coastal Beaches", "Old Phuket Heritage Town", "Patong Nightlife & Entertainment Strip", "Chalong Bay & Big Buddha Ridge"],
        "cultural_tips": ["Remove footwear before entering Thai homes and temples.", "Never touch someone on the head.", "Bargain politely at street night markets."]
    },
    {
        "city": "Santorini",
        "country": "Greece",
        "vibes": ["Beach & Coastal Sun", "Romantic & Scenic Escapes"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Solo Traveler"],
        "paces": ["Relaxed (2 activities/day + ample downtime)"],
        "seasons": ["Summer (Jun - Aug)", "Spring (Mar - May)", "Autumn / Fall (Sep - Nov)"],
        "currency": "EUR",
        "symbol": "€",
        "daily_usd": 250.0,
        "tagline": "Whitewashed caldera villages, blue-domed churches, and fiery Aegean sunsets.",
        "highlights": ["Oia Sunset Clifftop Promenade", "Fira to Oia Caldera Rim Hike", "Red Beach & Akrotiri Bronze Age Ruins", "Catamaran Sunset Sailing with Greek BBQ"],
        "connectivity": "Santorini Airport (JTR) or high-speed ferry from Piraeus Athens",
        "why": "The ultimate romantic bucket-list escape featuring volcanic wine tastings and infinity caldera pools.",
        "clusters": ["Oia Village & Sunset Castle", "Fira Capital & Cable Car Port", "Imerovigli Caldera Heights", "Akrotiri & Perissa Black Sand Coast"],
        "cultural_tips": ["Do not climb onto private church domes for photos.", "Drink bottled mineral water.", "Afternoon siesta is honored in smaller villages."]
    },
    {
        "city": "Bali",
        "country": "Indonesia",
        "vibes": ["Beach & Coastal Sun", "Off-the-Beaten-Path Nature", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Solo Traveler", "Couple / Romantic", "Group of Friends", "Family with Kids"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Summer (Jun - Aug)", "Spring (Mar - May)", "Autumn / Fall (Sep - Nov)"],
        "currency": "IDR",
        "symbol": "Rp ",
        "daily_usd": 85.0,
        "tagline": "Lush jungle ravines, spiritual temples, surf breaks, and bohemian wellness cafes.",
        "highlights": ["Ubud Tegallalang Rice Terraces & Swing", "Uluwatu Sunset Clifftop Temple & Kecak Dance", "Nusa Penida Kelingking T-Rex Beach Boat Day", "Seminyak Beachfront Sunset Clubs"],
        "connectivity": "Ngurah Rai International Airport (DPS) in Denpasar",
        "why": "Incredible value for luxury villas, thriving digital nomad community for solo travelers, and spiritual wellness retreats.",
        "clusters": ["Ubud Cultural Heart & Monkey Forest", "Seminyak & Canggu Coast", "Uluwatu Cliffs & South Coast", "Sanur & Nusa Islands Ferry Gateway"],
        "cultural_tips": ["Wear sarong and sash at sacred temples.", "Watch your step for Canang Sari street offerings.", "Use Grab/Gojek or Bluebird metered taxis."]
    },
    {
        "city": "Goa",
        "country": "India",
        "vibes": ["Beach & Coastal Sun", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Group of Friends", "Solo Traveler", "Couple / Romantic"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Winter (Dec - Feb)", "Autumn / Fall (Sep - Nov)", "Spring (Mar - May)"],
        "currency": "INR",
        "symbol": "₹",
        "daily_usd": 55.0,
        "tagline": "Golden Arabian Sea shores, Portuguese colonial villas, and beach shacks.",
        "highlights": ["Anjuna & Vagator Sunset Beach Lounges", "Old Goa UNESCO Basilica of Bom Jesus", "Fontainhas Latin Quarter Heritage Walk", "Dudhsagar Waterfalls Jungle Jeep Safari"],
        "connectivity": "Dabolim (GOI) or Manohar International Airport (GOX)",
        "why": "Vibrant party scene for friends, serene South Goa beaches for couples, and Portuguese seafood gastronomy.",
        "clusters": ["North Goa Coast (Anjuna, Vagator & Baga)", "Fontainhas Heritage Quarter Panaji", "South Goa Serenity (Palolem & Agonda)", "Old Goa Churches & Spice Plantations"],
        "cultural_tips": ["Renting a scooter requires an active driving license.", "Support local beach shacks and clean up beach plastic.", "Respect local heritage neighborhoods."]
    },

    # 3. Vibrant Urban Megacity
    {
        "city": "Tokyo",
        "country": "Japan",
        "vibes": ["Vibrant Urban Megacity", "Foodie Paradise & Wine Tasting", "Historic & Cultural Heritage"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Solo Traveler", "Group of Friends", "Family with Kids", "Couple / Romantic"],
        "paces": ["Fast-Paced (Packed highlights from dawn to late night)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Spring (Mar - May)", "Autumn / Fall (Sep - Nov)", "Winter (Dec - Feb)"],
        "currency": "JPY",
        "symbol": "¥",
        "daily_usd": 160.0,
        "tagline": "Futuristic neon skyscrapers, Michelin-starred ramen, and tranquil Shinto shrines.",
        "highlights": ["Shibuya Scramble Crossing & Sky Observatory", "Shinjuku Golden Gai Micro-Bars & Omoide Yokocho", "teamLab Borderless Immersive Digital Art", "Senso-ji Asakusa Historic Temple & Nakamise Stalls"],
        "connectivity": "Haneda (HND) and Narita (NRT) Airports; Yamanote rail loop",
        "why": "Unmatched safety for solo travelers, boundless pop-culture for friends, and world's highest concentration of fine dining.",
        "clusters": ["Shibuya & Harajuku Youth Hub", "Shinjuku & Kabukicho Night Lights", "Asakusa & Ueno Cultural Old Town", "Ginza & Tokyo Station Luxury Strip"],
        "cultural_tips": ["Never walk and eat on public streets simultaneously.", "Stand on the left side of escalators in Tokyo.", "No tipping in Japan—exceptional service is standard."]
    },
    {
        "city": "New York City",
        "country": "USA",
        "vibes": ["Vibrant Urban Megacity", "Historic & Cultural Heritage"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Solo Traveler", "Group of Friends", "Couple / Romantic", "Business & Leisure (Bleisure)"],
        "paces": ["Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Autumn / Fall (Sep - Nov)", "Spring (Mar - May)", "Winter (Dec - Feb)"],
        "currency": "USD",
        "symbol": "$",
        "daily_usd": 280.0,
        "tagline": "The electrifying cultural and culinary crossroads of the world.",
        "highlights": ["Broadway Theatre & Times Square Lights", "Central Park Stroll & The Met Museum", "Brooklyn Bridge Walk & DUMBO Waterfront", "High Line Elevated Park & Chelsea Market"],
        "connectivity": "JFK, EWR, and LGA airports; 24/7 Subway transit system",
        "why": "Limitless cultural energy, world-famous museums, iconic skyline viewpoints, and unmatched diversity.",
        "clusters": ["Midtown & Broadway Theater District", "Lower Manhattan & Financial District", "Greenwich Village & SoHo Boutiques", "DUMBO & Brooklyn Waterfront"],
        "cultural_tips": ["Keep to the right when walking on crowded sidewalks.", "Standard restaurant tipping is 18-22%.", "Tap to pay with OMNY on subways and buses."]
    },
    {
        "city": "Barcelona",
        "country": "Spain",
        "vibes": ["Vibrant Urban Megacity", "Beach & Coastal Sun", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Group of Friends", "Couple / Romantic", "Solo Traveler"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Spring (Mar - May)", "Summer (Jun - Aug)", "Autumn / Fall (Sep - Nov)"],
        "currency": "EUR",
        "symbol": "€",
        "daily_usd": 150.0,
        "tagline": "Gaudí architectural wonderland meets vibrant Mediterranean beachfront nightlife.",
        "highlights": ["Sagrada Família Basílica Architectural Marvel", "Park Güell Mosaic Sculptures & Skyline View", "Gothic Quarter Tapas & Sangria Crawl", "Barceloneta Beach Promenade & Sunset Drinks"],
        "connectivity": "Barcelona El Prat (BCN) Airport; AVE high-speed rail",
        "why": "Walkable pedestrian promenades, late-night dining culture, modernist art, and urban beachfront relaxation.",
        "clusters": ["Gothic Quarter & Born Historic Alleys", "Eixample & Gaudí Modernist Boulevard", "Gràcia Artisan Square & Park Güell", "Barceloneta & Olympic Port Promenade"],
        "cultural_tips": ["Dinner starts late (typically 9:00 PM onwards).", "Pre-book Sagrada Família admission weeks ahead.", "Be alert against pickpockets in crowded tourist zones."]
    },
    {
        "city": "Dubai",
        "country": "UAE",
        "vibes": ["Vibrant Urban Megacity", "Romantic & Scenic Escapes"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Family with Kids", "Couple / Romantic", "Business & Leisure (Bleisure)"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Winter (Dec - Feb)", "Spring (Mar - May)", "Autumn / Fall (Sep - Nov)"],
        "currency": "AED",
        "symbol": "AED ",
        "daily_usd": 220.0,
        "tagline": "Hyper-modern architectural marvels rising from Arabian desert dunes.",
        "highlights": ["Burj Khalifa 148th Floor Observatory & Dancing Fountain", "Red Dune Desert 4x4 Safari with Bedouin BBQ", "Dubai Marina Yacht Cruise & JBR Walk", "Old Dubai Creek Gold & Spice Souk Abra Ride"],
        "connectivity": "Dubai International (DXB); Dubai Metro driverless network",
        "why": "Pristine luxury, extraordinary architectural ambition, family theme parks, and Michelin-starred dining.",
        "clusters": ["Downtown Dubai & Burj Khalifa", "Dubai Marina & Jumeirah Beach Residence", "Old Deira & Al Fahidi Historical Neighborhood", "Palm Jumeirah & Atlantis Island"],
        "cultural_tips": ["Dress respectfully in government buildings and traditional souks.", "Public transport has women & children-only carriages.", "Tipping 10-15% is customary."]
    },
    {
        "city": "London",
        "country": "UK",
        "vibes": ["Vibrant Urban Megacity", "Historic & Cultural Heritage"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Family with Kids", "Solo Traveler", "Couple / Romantic", "Group of Friends"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Spring (Mar - May)", "Summer (Jun - Aug)", "Autumn / Fall (Sep - Nov)"],
        "currency": "GBP",
        "symbol": "£",
        "daily_usd": 240.0,
        "tagline": "Centuries of royal heritage, world-class free museums, and vibrant theater.",
        "highlights": ["British Museum & Tower of London Jewels", "West End Musical Theater Production", "Borough Market Artisan Food Feast", "Thames River Cruise from Westminster to Greenwich"],
        "connectivity": "London Heathrow (LHR), Gatwick (LGW); London Underground Tube network",
        "why": "World-leading cultural institutions with free admission, family-friendly parks, and iconic royal landmarks.",
        "clusters": ["Westminster & Buckingham Palace Core", "Covent Garden & West End Theaters", "City of London & Tower Bridge", "South Bank & Borough Market Waterfront"],
        "cultural_tips": ["Always stand on the right on Tube escalators.", "Tap credit card or Oyster for all transit.", "Mind the gap between train and platform."]
    },

    # 4. Historic & Cultural Heritage
    {
        "city": "Kyoto",
        "country": "Japan",
        "vibes": ["Historic & Cultural Heritage", "Romantic & Scenic Escapes", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Solo Traveler", "Family with Kids"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Spring (Mar - May)", "Autumn / Fall (Sep - Nov)", "Winter (Dec - Feb)"],
        "currency": "JPY",
        "symbol": "¥",
        "daily_usd": 140.0,
        "tagline": "Ancient Shinto shrines, tranquil bamboo groves, and sublime kaiseki dining.",
        "highlights": ["Fushimi Inari 10,000 Vermilion Torii Gates", "Arashiyama Bamboo Forest & Sagano Romantic Train", "Gion Historic Wooden Tea Houses & Geisha Alleys", "Kinkaku-ji Golden Pavilion & Zen Rock Gardens"],
        "connectivity": "Shinkansen bullet train from Tokyo; Kansai International (KIX)",
        "why": "Unrivaled spiritual serenity, centuries of preserved wooden architecture, and refined seasonal culinary traditions.",
        "clusters": ["Higashiyama & Gion", "Arashiyama & Sagano", "Kinkaku-ji & Northern Hills", "Central Kyoto & Fushimi Inari"],
        "cultural_tips": ["Remove footwear when stepping onto tatami mats.", "Never photograph geishas or maikos aggressively.", "No tipping in restaurants."]
    },
    {
        "city": "Rome",
        "country": "Italy",
        "vibes": ["Historic & Cultural Heritage", "Foodie Paradise & Wine Tasting", "Romantic & Scenic Escapes"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Family with Kids", "Solo Traveler"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Spring (Mar - May)", "Autumn / Fall (Sep - Nov)", "Winter (Dec - Feb)"],
        "currency": "EUR",
        "symbol": "€",
        "daily_usd": 170.0,
        "tagline": "An open-air living museum of imperial gladiators, baroque fountains, and carbonara.",
        "highlights": ["Colosseum & Roman Forum Ancient Ruins", "Vatican City & Sistine Chapel Frescoes", "Trevi Fountain Coin Toss & Pantheon Dome", "Trastevere Cobblestone Trattoria Food Tour"],
        "connectivity": "Rome Fiumicino Airport (FCO); Termini central rail station",
        "why": "Unrivaled ancient history at every corner, world-famous gelato, and unforgettable cobblestone evening strolls.",
        "clusters": ["Colosseum & Ancient Imperial Forum", "Vatican City & Prati District", "Trevi, Pantheon & Navona Baroque Hub", "Trastevere & Tiber Island Quarter"],
        "cultural_tips": ["Dress modestly for Vatican and basilicas (cover shoulders & knees).", "Order cappuccino before 11 AM only.", "Drink fresh water from city 'Nasone' fountains."]
    },
    {
        "city": "Jaipur & Rajasthan",
        "country": "India",
        "vibes": ["Historic & Cultural Heritage", "Romantic & Scenic Escapes"],
        "budgets": ["Budget", "Moderate", "Luxury"],
        "parties": ["Family with Kids", "Couple / Romantic", "Group of Friends"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Relaxed (2 activities/day + ample downtime)"],
        "seasons": ["Winter (Dec - Feb)", "Autumn / Fall (Sep - Nov)", "Spring (Mar - May)"],
        "currency": "INR",
        "symbol": "₹",
        "daily_usd": 75.0,
        "tagline": "The royal Pink City of palatial fortresses, gem bazaars, and opulent heritage.",
        "highlights": ["Amer Fort Clifftop Ramparts & Mirror Palace", "Hawa Mahal Palace of the Winds Honeycomb Facade", "City Palace & Jantar Mantar Astronomical Observatory", "Nahargarh Fort Sunset Over the Pink City"],
        "connectivity": "Jaipur International Airport (JAI); Vande Bharat Express from Delhi",
        "why": "Living fairytale palaces, grand royal hospitality, colorful textiles, and majestic mountain fortresses.",
        "clusters": ["Old Walled Pink City", "Amer & Jaigarh Fort Ridge", "Civil Lines & Royal Palaces", "C-Scheme Cafes & Bazaars"],
        "cultural_tips": ["Remove footwear before entering shrines and heritage sanctums.", "Negotiate gently at open bazaars.", "Stay hydrated and drink filtered mineral water."]
    },
    {
        "city": "Cairo & Giza",
        "country": "Egypt",
        "vibes": ["Historic & Cultural Heritage", "Off-the-Beaten-Path Nature"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Solo Traveler", "Group of Friends", "Family with Kids"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Winter (Dec - Feb)", "Autumn / Fall (Sep - Nov)", "Spring (Mar - May)"],
        "currency": "EGP",
        "symbol": "E£",
        "daily_usd": 70.0,
        "tagline": "Timeless Great Pyramids, Sphinx mysteries, and the fertile Nile Valley.",
        "highlights": ["Great Pyramids of Giza & Great Sphinx Camel Trek", "Grand Egyptian Museum Treasures of Tutankhamun", "Khan el-Khalili Ancient Lantern Souk", "Nile River Sunset Felucca Sail"],
        "connectivity": "Cairo International (CAI); Cairo Metro network",
        "why": "The ultimate wonder of the ancient world with astonishing monuments and vibrant Middle Eastern market energy.",
        "clusters": ["Giza Plateau & Pyramid Ridge", "Downtown Cairo & Tahrir Museum", "Islamic Cairo & Khan el-Khalili Bazaar", "Zamalek Island & Nile Promenade"],
        "cultural_tips": ["Modest dress is respected, particularly around historic mosques.", "Tipping ('baksheesh') is an integral part of service culture.", "Cross busy Cairo avenues with locals."]
    },

    # 5. Foodie Paradise & Wine Tasting
    {
        "city": "Paris",
        "country": "France",
        "vibes": ["Foodie Paradise & Wine Tasting", "Romantic & Scenic Escapes", "Historic & Cultural Heritage"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Couple / Romantic", "Solo Traveler", "Family with Kids"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Relaxed (2 activities/day + ample downtime)"],
        "seasons": ["Spring (Mar - May)", "Autumn / Fall (Sep - Nov)", "Summer (Jun - Aug)"],
        "currency": "EUR",
        "symbol": "€",
        "daily_usd": 220.0,
        "tagline": "Haute cuisine bistros, golden boulevards, and timeless artistic masterpieces.",
        "highlights": ["Louvre Museum & Mona Lisa Masterpieces", "Eiffel Tower Sunset Illumination from Champ de Mars", "Montmartre Sacré-Cœur Artist Quarter Stroll", "Seine River Candlelit Dinner Cruise"],
        "connectivity": "Charles de Gaulle (CDG) and Orly (ORY) airports; extensive Metro network",
        "why": "The world's capital of gastronomy, romantic sidewalk cafes, legendary boulangeries, and world-class museums.",
        "clusters": ["Le Marais & Île de la Cité", "Montmartre & 18th Arr.", "Latin Quarter & Saint-Germain", "Eiffel Tower & Champs-Élysées"],
        "cultural_tips": ["Always say 'Bonjour' upon entering any boutique or cafe.", "Keep metro tickets until you exit the station.", "Take your time dining; bistros never rush patrons."]
    },
    {
        "city": "Oaxaca",
        "country": "Mexico",
        "vibes": ["Foodie Paradise & Wine Tasting", "Historic & Cultural Heritage", "Off-the-Beaten-Path Nature"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Solo Traveler", "Couple / Romantic", "Group of Friends"],
        "paces": ["Relaxed (2 activities/day + ample downtime)", "Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Autumn / Fall (Sep - Nov)", "Winter (Dec - Feb)", "Spring (Mar - May)"],
        "currency": "MXN",
        "symbol": "Mex$",
        "daily_usd": 80.0,
        "tagline": "The culinary soul of Mexico: rich moles, artisanal mezcal, and indigenous weaving.",
        "highlights": ["Monte Albán Zapotec Pyramids & Valley Vista", "Tlacolula Sunday Indigenous Market & Smoke Alley", "Artisanal Mezcal Distillery Tour in Matatlán", "Santo Domingo Church & Botanical Garden Stroll"],
        "connectivity": "Oaxaca International Airport (OAX) via Mexico City",
        "why": "Unbeatable culinary depth, colorful colonial facades, warm indigenous heritage, and craft mezcal tastings.",
        "clusters": ["Centro Histórico & Zócalo Plaza", "Santo Domingo & Jalatlaco Bohemian Quarter", "Monte Albán Ancient Ridge", "Tlacolula Valley & Mezcal Trail"],
        "cultural_tips": ["Try traditional street food like tlayudas and memelas.", "Respect indigenous artisans when photographing.", "Mezcal is meant to be sipped slowly, not shot."]
    },

    # 6. Off-the-Beaten-Path Nature & Adventure
    {
        "city": "Reykjavik & Golden Circle",
        "country": "Iceland",
        "vibes": ["Off-the-Beaten-Path Nature", "Mountains, Hiking & Serenity"],
        "budgets": ["Moderate", "Luxury"],
        "parties": ["Group of Friends", "Couple / Romantic", "Solo Traveler"],
        "paces": ["Moderate (3-4 activities with balanced breaks)", "Fast-Paced (Packed highlights from dawn to late night)"],
        "seasons": ["Winter (Dec - Feb)", "Summer (Jun - Aug)", "Autumn / Fall (Sep - Nov)"],
        "currency": "ISK",
        "symbol": "kr ",
        "daily_usd": 230.0,
        "tagline": "Land of fire and ice: geothermal geysers, thundering waterfalls, and Northern Lights.",
        "highlights": ["Blue Lagoon Geothermal Silica Spa", "Golden Circle: Gullfoss Waterfall & Strokkur Geyser", "Thingvellir Tectonic Rift Walk", "Aurora Borealis Northern Lights Jeep Expedition"],
        "connectivity": "Keflavik International Airport (KEF); Ring Road highway network",
        "why": "Surreal otherworldly volcanic landscapes, majestic waterfalls, soothing thermal pools, and celestial aurora displays.",
        "clusters": ["Reykjavik Old Harbor & Hallgrímskirkja", "Golden Circle Geothermal Valley", "Reykjanes Peninsula & Blue Lagoon", "South Coast Glacier & Black Sand Beach"],
        "cultural_tips": ["Iceland is almost 100% cashless; cards accepted everywhere.", "Always shower with soap before entering thermal lagoons.", "Check road.is and vedur.is daily for weather alerts."]
    },
    {
        "city": "Cape Town",
        "country": "South Africa",
        "vibes": ["Off-the-Beaten-Path Nature", "Beach & Coastal Sun", "Foodie Paradise & Wine Tasting"],
        "budgets": ["Budget", "Moderate"],
        "parties": ["Group of Friends", "Solo Traveler", "Couple / Romantic"],
        "paces": ["Moderate (3-4 activities with balanced breaks)"],
        "seasons": ["Summer (Jun - Aug)", "Winter (Dec - Feb)", "Spring (Mar - May)"],
        "currency": "ZAR",
        "symbol": "R ",
        "daily_usd": 95.0,
        "tagline": "Dramatic Table Mountain rising between Atlantic surf and lush Cape winelands.",
        "highlights": ["Table Mountain Cableway 360-degree Summit", "Boulders Beach African Penguin Colony", "Cape of Good Hope Oceanic Scenic Drive", "Stellenbosch & Franschhoek Historic Wine Tram"],
        "connectivity": "Cape Town International Airport (CPT); reliable Uber rideshare",
        "why": "Astonishing natural scenery, ocean adventures, world-class vineyard dining, and remarkable affordability.",
        "clusters": ["V&A Waterfront & City Bowl", "Camps Bay & Clifton Coastal Beaches", "Kirstenbosch Gardens & Constantia Wine Valley", "Cape Point & Boulders Peninsula"],
        "cultural_tips": ["Use Uber for convenient and safe city navigation.", "Carry a windbreaker as Cape weather can shift rapidly.", "Tipping 10-15% is standard for hospitality staff."]
    }
]

# Quick Map of destinations by name for fast lookup
DESTINATION_METADATA = {d["city"]: d for d in DESTINATION_CATALOG}
# Also add common alias keys
DESTINATION_METADATA["Kyoto, Japan"] = DESTINATION_METADATA["Kyoto"]
DESTINATION_METADATA["Paris, France"] = DESTINATION_METADATA["Paris"]
DESTINATION_METADATA["Barcelona, Spain"] = DESTINATION_METADATA["Barcelona"]
DESTINATION_METADATA["Amalfi Coast, Italy"] = DESTINATION_METADATA["Amalfi Coast"]
DESTINATION_METADATA["Bali, Indonesia"] = DESTINATION_METADATA["Bali"]
DESTINATION_METADATA["Jaipur & Rajasthan, India"] = DESTINATION_METADATA["Jaipur & Rajasthan"]
DESTINATION_METADATA["Tokyo, Japan"] = DESTINATION_METADATA["Tokyo"]
DESTINATION_METADATA["New York City, USA"] = DESTINATION_METADATA["New York City"]
DESTINATION_METADATA["Rome, Italy"] = DESTINATION_METADATA["Rome"]
DESTINATION_METADATA["London, UK"] = DESTINATION_METADATA["London"]
DESTINATION_METADATA["Dubai, UAE"] = DESTINATION_METADATA["Dubai"]
