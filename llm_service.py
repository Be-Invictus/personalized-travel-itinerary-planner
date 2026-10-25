"""
LLM Service Layer: Handles Gemini, Groq, structured JSON output, prompt engineering,
and resilient offline demo/mock generation.
"""

import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from config import CURRENCIES, DESTINATION_METADATA, BUDGET_TIERS
from models import (
    Itinerary, DayPlan, ActivitySlot, DestinationRecommendation, EmergencyInfo
)


def _clean_json_string(raw_str: str) -> str:
    """Extracts clean JSON from raw LLM output even if surrounded by markdown or commentary."""
    text = raw_str.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    else:
        # Search for first { or [ and last } or ]
        first_bracket = min((text.find('{'), text.find('[')))
        if first_bracket != -1:
            last_bracket = max((text.rfind('}'), text.rfind(']')))
            if last_bracket > first_bracket:
                text = text[first_bracket:last_bracket + 1]
    
    # Clean common trailing commas
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


class LLMService:
    """Unified AI service supporting Google Gemini, Groq, and intelligent Demo Mode."""

    def __init__(self, provider: str = "Demo", api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY") or ""
        self.model = model
        self.is_demo = (provider == "Demo" or not self.api_key.strip())

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Invokes Google Gemini with fallback between google-genai and google.generativeai."""
        # Try google-genai first
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key)
            model_name = self.model or "gemini-2.5-flash"
            
            config = types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e_new:
            # Fallback to google.generativeai
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                model_name = self.model or "gemini-1.5-flash"
                model_inst = legacy_genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction if system_instruction else None
                )
                res = model_inst.generate_content(
                    prompt,
                    generation_config={"temperature": 0.4, "response_mime_type": "application/json"}
                )
                return res.text
            except Exception as e_old:
                raise RuntimeError(f"Gemini API invocation failed: {str(e_new)} | Legacy error: {str(e_old)}")

    def _call_groq(self, prompt: str, system_instruction: str = "") -> str:
        """Invokes Groq Cloud API."""
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            model_name = self.model or "llama-3.3-70b-versatile"
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API invocation failed: {str(e)}")

    def generate_raw(self, prompt: str, system_instruction: str = "") -> str:
        """Routes prompt to appropriate provider or raises for demo mode handling."""
        if self.is_demo:
            raise ValueError("Demo mode active; use mock generator.")
        
        if self.provider == "Gemini":
            return self._call_gemini(prompt, system_instruction)
        elif self.provider == "Groq":
            return self._call_groq(prompt, system_instruction)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # =========================================================================
    # TAB 1: DESTINATION RECOMMENDATIONS
    # =========================================================================

    def recommend_destinations(self, mood: str, budget: str, season: str, party: str, interests: List[str]) -> List[DestinationRecommendation]:
        """Generates 3 matching destination recommendations."""
        if self.is_demo:
            return self._mock_recommendations(mood, budget, season)

        system_instruction = (
            "You are a master travel curator. Recommend exactly 3 distinct destinations matching the user's "
            "vibe, budget tier, season, party type, and interests. Return strictly valid JSON array of objects."
        )

        prompt = f"""
        Recommend 3 extraordinary travel destinations based on:
        - Travel Mood / Vibe: {mood}
        - Budget Tier: {budget}
        - Travel Season / Month: {season}
        - Travel Party: {party}
        - Interests: {', '.join(interests) if interests else 'General sightseeing'}

        Respond ONLY with a JSON array conforming to this exact structure:
        [
          {{
            "city": "City Name",
            "country": "Country",
            "tagline": "Punchy evocative tagline",
            "match_score": 96,
            "vibe_category": "{mood}",
            "best_season": "October to April",
            "estimated_daily_usd": 120.0,
            "top_highlights": ["Highlight 1", "Highlight 2", "Highlight 3", "Highlight 4"],
            "transit_connectivity": "Direct flights from major hubs; high-speed rail",
            "why_you_will_love_it": "Why this specifically suits their travel party and budget."
          }}
        ]
        """
        try:
            raw_output = self.generate_raw(prompt, system_instruction)
            cleaned = _clean_json_string(raw_output)
            data = json.loads(cleaned)
            if isinstance(data, dict) and "destinations" in data:
                data = data["destinations"]
            return [DestinationRecommendation(**item) for item in data[:3]]
        except Exception as e:
            # Fallback to high-quality procedural mock if API times out or fails
            return self._mock_recommendations(mood, budget, season)

    # =========================================================================
    # TAB 2: GEOGRAPHIC CLUSTERED ITINERARY GENERATOR
    # =========================================================================

    def generate_itinerary(
        self,
        destination: str,
        duration_days: int,
        start_date: str,
        budget_level: str,
        travel_party: str,
        pace: str,
        interests: List[str]
    ) -> Itinerary:
        """Generates a comprehensive day-by-day itinerary with geographic clustering and costs."""
        if self.is_demo:
            return self._mock_itinerary(
                destination, duration_days, start_date, budget_level, travel_party, pace, interests
            )

        # Determine target currency & rates
        meta = DESTINATION_METADATA.get(destination, {})
        curr_code = meta.get("currency", "USD")
        curr_info = CURRENCIES.get(curr_code, CURRENCIES["USD"])
        usd_rate = curr_info["rate_from_usd"]
        inr_rate = CURRENCIES["INR"]["rate_from_usd"]
        symbol = curr_info["symbol"]

        system_instruction = (
            "You are a senior full-stack travel SaaS architect and master geographic route optimizer. "
            "Your critical rule is GEOGRAPHIC CLUSTERING: every single day must strictly cluster attractions, "
            "restaurants, and activities within ONE specific geographic neighborhood/district to eliminate cross-city "
            "backtracking and minimize transit fatigue. Return strictly valid JSON."
        )

        prompt = f"""
        Create a detailed {duration_days}-day itinerary for {destination}.
        Trip Parameters:
        - Start Date: {start_date}
        - Budget Level: {budget_level}
        - Travel Party: {travel_party}
        - Travel Pace: {pace}
        - Specific Interests: {', '.join(interests) if interests else 'Culture, Food, Sights'}
        - Local Currency: {curr_code} ({symbol}), Rate: 1 USD = {usd_rate} {curr_code}

        CRITICAL GEOGRAPHIC CLUSTERING INSTRUCTIONS:
        1. Each day MUST focus on a distinct neighborhood / zone (e.g. Day 1: Historic Old Town, Day 2: Waterfront/Harbor).
        2. Sequence each day with 4 slots: 'Morning', 'Lunch', 'Afternoon', 'Evening'.
        3. All 4 slots for that day MUST be located within or adjacent to that day's neighborhood cluster.
        4. State the walking/transit recommendation in each slot (e.g., '5-min walk down Royal Street' or 'Short 2-stop tram #4').
        5. Provide realistic itemized estimated costs per slot in local currency ({curr_code}) matching the {budget_level} budget tier.

        Return ONLY a JSON object with this exact schema:
        {{
          "trip_title": "Grand Explorer: {destination}",
          "destination": "{destination}",
          "country": "{meta.get('country', 'International')}",
          "local_currency_code": "{curr_code}",
          "local_currency_symbol": "{symbol}",
          "usd_exchange_rate": {usd_rate},
          "inr_exchange_rate": {inr_rate},
          "duration_days": {duration_days},
          "start_date": "{start_date}",
          "end_date": "calculated end date",
          "budget_level": "{budget_level}",
          "travel_party": "{travel_party}",
          "pace": "{pace}",
          "interests": {json.dumps(interests)},
          "days": [
            {{
              "day_number": 1,
              "date_str": "{start_date}",
              "theme": "Theme title for the day",
              "neighborhood_cluster": "Name of district/cluster",
              "transit_summary": "Geographic transit tip for zero backtracking",
              "slots": [
                {{
                  "slot_id": "day1_morning",
                  "time_slot": "Morning",
                  "time_range": "09:00 - 12:00",
                  "title": "Specific attraction name",
                  "neighborhood": "Cluster district",
                  "description": "Engaging activity details",
                  "transit_tip": "Walking/transit route notes",
                  "cost_local": 25.0,
                  "cost_usd": 25.0,
                  "cost_inr": 2100.0,
                  "tags": ["Culture", "Landmark"],
                  "booking_required": false
                }},
                {{
                  "slot_id": "day1_lunch",
                  "time_slot": "Lunch",
                  "time_range": "12:30 - 14:00",
                  "title": "Specific authentic eatery / dish",
                  "neighborhood": "Cluster district",
                  "description": "Cuisine notes, must-try dish, dietary options",
                  "transit_tip": "Walking distance from morning spot",
                  "cost_local": 20.0,
                  "cost_usd": 20.0,
                  "cost_inr": 1700.0,
                  "tags": ["Culinary", "Local Favorite"],
                  "booking_required": false
                }},
                {{
                  "slot_id": "day1_afternoon",
                  "time_slot": "Afternoon",
                  "time_range": "14:30 - 17:30",
                  "title": "Afternoon cultural immersion or park",
                  "neighborhood": "Cluster district",
                  "description": "Activity details",
                  "transit_tip": "Short stroll",
                  "cost_local": 15.0,
                  "cost_usd": 15.0,
                  "cost_inr": 1275.0,
                  "tags": ["Scenic", "Leisure"],
                  "booking_required": false
                }},
                {{
                  "slot_id": "day1_evening",
                  "time_slot": "Evening",
                  "time_range": "18:30 - 22:00",
                  "title": "Evening dining and night atmosphere",
                  "neighborhood": "Cluster district",
                  "description": "Dinner venue and evening stroll/show",
                  "transit_tip": "Walk within cluster",
                  "cost_local": 40.0,
                  "cost_usd": 40.0,
                  "cost_inr": 3400.0,
                  "tags": ["Dining", "Nightlife"],
                  "booking_required": true
                }}
              ]
            }}
          ],
          "packing_checklist": ["Item 1", "Item 2", "Item 3", "Item 4"],
          "cultural_tips": ["Tip 1", "Tip 2", "Tip 3"],
          "emergency_info": {{
            "police_number": "112",
            "ambulance_number": "112",
            "tourist_helpline": "Available 24/7",
            "embassy_note": "Consulates located in main administrative sector",
            "local_hospital": "Nearest international clinic",
            "emergency_phrases": ["Help: Aide / Tasukete", "Doctor: Medico / Ishi"]
          }}
        }}
        """

        try:
            raw_output = self.generate_raw(prompt, system_instruction)
            cleaned = _clean_json_string(raw_output)
            data = json.loads(cleaned)
            itinerary = self._process_itinerary_costs(data, usd_rate, inr_rate)
            return itinerary
        except Exception as e:
            # Fallback to high-fidelity procedural itinerary
            return self._mock_itinerary(
                destination, duration_days, start_date, budget_level, travel_party, pace, interests
            )

    # =========================================================================
    # TAB 3: DYNAMIC ACTIVITY SWAP ENGINE
    # =========================================================================

    def swap_activity_slot(
        self,
        current_slot: ActivitySlot,
        day_theme: str,
        neighborhood_cluster: str,
        destination: str,
        swap_intent: str,
        budget_level: str,
        currency_code: str,
        usd_rate: float,
        inr_rate: float
    ) -> ActivitySlot:
        """Regenerates a single slot based on user modification intent while preserving clustering."""
        if self.is_demo:
            return self._mock_swap_slot(
                current_slot, neighborhood_cluster, swap_intent, currency_code, usd_rate, inr_rate
            )

        system_instruction = (
            "You are an AI travel concierge specializing in instant activity customization. "
            "The user wants to replace an existing activity slot with a new one matching their specific custom vibe, "
            "dietary need, or pace, while STRICTLY REMAINING within the same neighborhood cluster."
        )

        prompt = f"""
        Replace this current activity slot in {destination}:
        - Slot Time: {current_slot.time_slot} ({current_slot.time_range})
        - Current Title: {current_slot.title}
        - Target Neighborhood Cluster: {neighborhood_cluster}
        - Day Theme: {day_theme}
        - User Swap Intent / Requirement: "{swap_intent}"
        - Budget Tier: {budget_level}
        - Currency: {currency_code} (1 USD = {usd_rate} {currency_code})

        Return ONLY a JSON object for the replacement ActivitySlot conforming to this schema:
        {{
          "slot_id": "{current_slot.slot_id}",
          "time_slot": "{current_slot.time_slot}",
          "time_range": "{current_slot.time_range}",
          "title": "New Activity Name",
          "neighborhood": "{neighborhood_cluster}",
          "description": "Engaging description fulfilling user swap request",
          "transit_tip": "Walking route within {neighborhood_cluster}",
          "cost_local": 25.0,
          "tags": ["Updated Tag 1", "Updated Tag 2"],
          "booking_required": false
        }}
        """

        try:
            raw_output = self.generate_raw(prompt, system_instruction)
            cleaned = _clean_json_string(raw_output)
            data = json.loads(cleaned)
            cost_local = float(data.get("cost_local", current_slot.cost_local))
            cost_usd = round(cost_local / usd_rate, 2) if usd_rate > 0 else cost_local
            cost_inr = round(cost_usd * inr_rate, 2)

            return ActivitySlot(
                slot_id=current_slot.slot_id,
                time_slot=data.get("time_slot", current_slot.time_slot),
                time_range=data.get("time_range", current_slot.time_range),
                title=data.get("title", f"Customized {current_slot.time_slot}"),
                neighborhood=data.get("neighborhood", neighborhood_cluster),
                description=data.get("description", "Tailored experience matching your custom vibe."),
                transit_tip=data.get("transit_tip", f"Walking distance in {neighborhood_cluster}"),
                cost_local=cost_local,
                cost_usd=cost_usd,
                cost_inr=cost_inr,
                tags=data.get("tags", ["Customized", swap_intent[:15]]),
                booking_required=data.get("booking_required", False)
            )
        except Exception:
            return self._mock_swap_slot(
                current_slot, neighborhood_cluster, swap_intent, currency_code, usd_rate, inr_rate
            )

    # =========================================================================
    # INTERNAL HELPERS & PROCEDURAL DEMO ENGINE
    # =========================================================================

    def _process_itinerary_costs(self, data: Dict[str, Any], usd_rate: float, inr_rate: float) -> Itinerary:
        """Calculates running totals, USD, and INR conversions for each slot and day."""
        total_local = 0.0
        total_usd = 0.0
        total_inr = 0.0

        days_list = []
        for day_dict in data.get("days", []):
            d_local = 0.0
            slots_list = []
            cluster = day_dict.get("neighborhood_cluster", "Central District")
            
            for slot_dict in day_dict.get("slots", []):
                c_loc = float(slot_dict.get("cost_local", 20.0))
                c_usd = round(c_loc / usd_rate, 2) if usd_rate > 0 else c_loc
                c_inr = round(c_usd * inr_rate, 2)
                
                slot = ActivitySlot(
                    slot_id=slot_dict.get("slot_id", f"day{day_dict.get('day_number', 1)}_{slot_dict.get('time_slot','slot')}"),
                    time_slot=slot_dict.get("time_slot", "Morning"),
                    time_range=slot_dict.get("time_range", "09:00 - 12:00"),
                    title=slot_dict.get("title", "Attraction"),
                    neighborhood=slot_dict.get("neighborhood", cluster),
                    description=slot_dict.get("description", "Scenic exploration"),
                    transit_tip=slot_dict.get("transit_tip", "Walk nearby"),
                    cost_local=c_loc,
                    cost_usd=c_usd,
                    cost_inr=c_inr,
                    tags=slot_dict.get("tags", ["Sightseeing"]),
                    booking_required=slot_dict.get("booking_required", False)
                )
                slots_list.append(slot)
                d_local += c_loc

            d_usd = round(d_local / usd_rate, 2) if usd_rate > 0 else d_local
            d_inr = round(d_usd * inr_rate, 2)

            day_plan = DayPlan(
                day_number=day_dict.get("day_number", 1),
                date_str=day_dict.get("date_str", "2026-11-01"),
                theme=day_dict.get("theme", "Exploration"),
                neighborhood_cluster=cluster,
                transit_summary=day_dict.get("transit_summary", "Cluster-based walk"),
                slots=slots_list,
                daily_cost_local=d_local,
                daily_cost_usd=d_usd,
                daily_cost_inr=d_inr
            )
            days_list.append(day_plan)
            total_local += d_local
            total_usd += d_usd
            total_inr += d_inr

        # Emergency info
        em_data = data.get("emergency_info", {})
        emergency = EmergencyInfo(
            police_number=em_data.get("police_number", "112"),
            ambulance_number=em_data.get("ambulance_number", "112"),
            tourist_helpline=em_data.get("tourist_helpline", "Local Visitor Center"),
            embassy_note=em_data.get("embassy_note", "Consult foreign ministry registration."),
            local_hospital=em_data.get("local_hospital", "City General Hospital"),
            emergency_phrases=em_data.get("emergency_phrases", ["Help!", "Where is the hospital?"])
        )

        return Itinerary(
            trip_title=data.get("trip_title", "Custom Travel Itinerary"),
            destination=data.get("destination", "World Destination"),
            country=data.get("country", "International"),
            local_currency_code=data.get("local_currency_code", "USD"),
            local_currency_symbol=data.get("local_currency_symbol", "$"),
            usd_exchange_rate=usd_rate,
            inr_exchange_rate=inr_rate,
            duration_days=data.get("duration_days", len(days_list)),
            start_date=data.get("start_date", "2026-11-01"),
            end_date=data.get("end_date", "2026-11-05"),
            budget_level=data.get("budget_level", "Moderate"),
            travel_party=data.get("travel_party", "Couple"),
            pace=data.get("pace", "Moderate"),
            interests=data.get("interests", []),
            days=days_list,
            total_cost_local=round(total_local, 2),
            total_cost_usd=round(total_usd, 2),
            total_cost_inr=round(total_inr, 2),
            target_budget_usd=data.get("duration_days", len(days_list)) * 140.0,
            packing_checklist=data.get("packing_checklist", ["Comfortable shoes", "Universal adapter", "Light layers", "Rain shell"]),
            cultural_tips=data.get("cultural_tips", ["Keep local currency on hand", "Respect sacred cultural sites", "Tipping practices vary"]),
            emergency_info=emergency
        )

    def _mock_recommendations(self, mood: str, budget: str, season: str) -> List[DestinationRecommendation]:
        """Provides high-quality realistic recommendations for Demo mode."""
        catalog = [
            DestinationRecommendation(
                city="Kyoto",
                country="Japan",
                tagline="Ancient shrines, tranquil bamboo groves, and sublime kaiseki dining.",
                match_score=98,
                vibe_category="Historic & Cultural Heritage",
                best_season="March-May (Spring Cherry Blossoms) or Oct-Nov (Vibrant Autumn Foliage)",
                estimated_daily_usd=110.0 if budget == "Budget" else (220.0 if budget == "Moderate" else 480.0),
                top_highlights=["Fushimi Inari 10,000 Torii Gates", "Arashiyama Bamboo Forest & Monkey Park", "Gion Historic Geisha District", "Nishiki Market Street Food"],
                transit_connectivity="Bullet Train (Shinkansen) from Tokyo; Kansai International Airport (KIX)",
                why_you_will_love_it="World-class public transit, incredible safety, and unforgettable blend of serene temples and artisan culinary culture."
            ),
            DestinationRecommendation(
                city="Amalfi Coast",
                country="Italy",
                tagline="Cliffside pastel villages tumbling into azure Mediterranean waters.",
                match_score=95,
                vibe_category="Beach & Coastal Sun",
                best_season="May to September (Sun-drenched Mediterranean warmth)",
                estimated_daily_usd=130.0 if budget == "Budget" else (260.0 if budget == "Moderate" else 650.0),
                top_highlights=["Positano Cliffside Terraces", "Ravello Villa Cimbrone Gardens", "Path of the Gods Panoramic Hike", "Capri Blue Grotto Boat Charter"],
                transit_connectivity="High-speed rail to Salerno or Naples, followed by scenic coastal ferry",
                why_you_will_love_it="Breathtaking coastal vistas, authentic lemon-infused pasta, and romantic sea-breeze sunsets."
            ),
            DestinationRecommendation(
                city="Barcelona",
                country="Spain",
                tagline="Gaudí architectural wonderland meets vibrant Mediterranean beachfront nightlife.",
                match_score=94,
                vibe_category="Vibrant Urban Megacity",
                best_season="April to June & September to November",
                estimated_daily_usd=85.0 if budget == "Budget" else (175.0 if budget == "Moderate" else 420.0),
                top_highlights=["Sagrada Família Basílica", "Park Güell Surreal Mosaic Park", "Gothic Quarter Tapas Crawl", "Barceloneta Sunset Promenade"],
                transit_connectivity="Barcelona El Prat (BCN) International Airport; AVE high-speed rail to Madrid & France",
                why_you_will_love_it="Late-night tapas culture, walkable pedestrian avenues, and awe-inspiring modernist architecture."
            )
        ]
        return catalog

    def _mock_itinerary(
        self,
        destination: str,
        duration_days: int,
        start_date: str,
        budget_level: str,
        travel_party: str,
        pace: str,
        interests: List[str]
    ) -> Itinerary:
        """Generates an intelligent, geographically clustered itinerary procedurally."""
        meta = DESTINATION_METADATA.get(destination, {
            "currency": "USD",
            "symbol": "$",
            "country": "International",
            "police": "112",
            "ambulance": "112",
            "hospital": "International Medical Center",
            "clusters": ["Historic Old Town", "Arts & Cultural District", "Waterfront & Harbour", "Hillside Viewpoint & Market"],
            "cultural_tips": ["Carry a light jacket and comfortable walking footwear.", "Keep small local cash for neighborhood stalls.", "Respect local photography customs."]
        })

        curr_code = meta["currency"]
        curr_info = CURRENCIES.get(curr_code, CURRENCIES["USD"])
        usd_rate = curr_info["rate_from_usd"]
        inr_rate = CURRENCIES["INR"]["rate_from_usd"]
        symbol = curr_info["symbol"]

        clusters = meta.get("clusters", ["Central Quarter", "West Waterfront", "East Hillside", "South Heritage"])
        
        # Budget scaling multiplier
        multiplier = 0.6 if budget_level == "Budget" else (1.0 if budget_level == "Moderate" else 2.5)

        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        days_list = []

        total_local = 0.0

        for day_idx in range(duration_days):
            day_num = day_idx + 1
            cur_date = start_dt + timedelta(days=day_idx)
            cluster = clusters[day_idx % len(clusters)]

            # Procedural theme based on cluster
            themes = [
                f"{cluster} Architectural Wonders & Heritage",
                f"{cluster} Culinary Flavors & Artisan Alleys",
                f"{cluster} Panoramic Views & Hidden Corners",
                f"{cluster} Vibrant Markets & Sunset Vistas"
            ]
            theme = themes[day_idx % len(themes)]

            # Slot activities crafted specifically for the cluster
            base_slots = [
                {
                    "slot_id": f"day{day_num}_morning",
                    "time_slot": "Morning",
                    "time_range": "09:00 - 12:00",
                    "title": f"Iconic Landmark & Exploration in {cluster}",
                    "neighborhood": cluster,
                    "description": f"Begin your day at the primary cultural anchor of {cluster}. Experience morning serenity, photograph historic facades, and avoid midday crowds.",
                    "transit_tip": f"Take the local metro/bus to {cluster} Central Station; short 4-min walk.",
                    "cost_local": round(15.0 * usd_rate * multiplier, 1),
                    "tags": ["Culture", "Landmark", "Heritage"],
                    "booking_required": True if budget_level == "Luxury" else False
                },
                {
                    "slot_id": f"day{day_num}_lunch",
                    "time_slot": "Lunch",
                    "time_range": "12:30 - 14:00",
                    "title": f"Authentic Regional Lunch at {cluster} Bistro",
                    "neighborhood": cluster,
                    "description": f"Enjoy farm-to-table seasonal specialties and signature dishes of {destination}. Dietary friendly options available.",
                    "transit_tip": "Scenic 3-minute stroll down the pedestrian lane from the morning landmark.",
                    "cost_local": round(18.0 * usd_rate * multiplier, 1),
                    "tags": ["Culinary", "Local Gastronomy"],
                    "booking_required": False
                },
                {
                    "slot_id": f"day{day_num}_afternoon",
                    "time_slot": "Afternoon",
                    "time_range": "14:30 - 17:30",
                    "title": f"Artisan Workshops & Garden Walk in {cluster}",
                    "neighborhood": cluster,
                    "description": f"Immerse yourself in boutique craft shops, tranquil courtyards, and local galleries clustered within {cluster}.",
                    "transit_tip": "All stops within 400m walking radius—zero transit transfers needed.",
                    "cost_local": round(12.0 * usd_rate * multiplier, 1),
                    "tags": ["Leisure", "Artisan", "Scenic"],
                    "booking_required": False
                },
                {
                    "slot_id": f"day{day_num}_evening",
                    "time_slot": "Evening",
                    "time_range": "18:30 - 22:00",
                    "title": f"Sunset Dinner & Atmosphere in {cluster}",
                    "neighborhood": cluster,
                    "description": f"Cap off Day {day_num} with ambient dining, crafted local beverages, and an evening promenade as illuminated lanterns light up {cluster}.",
                    "transit_tip": "Short stroll to the evening promenade; convenient taxi stand nearby.",
                    "cost_local": round(35.0 * usd_rate * multiplier, 1),
                    "tags": ["Dining", "Atmosphere", "Nightlife"],
                    "booking_required": True
                }
            ]

            processed_slots = []
            day_local = 0.0
            for s in base_slots:
                c_loc = s["cost_local"]
                c_usd = round(c_loc / usd_rate, 2)
                c_inr = round(c_usd * inr_rate, 2)
                act = ActivitySlot(
                    slot_id=s["slot_id"],
                    time_slot=s["time_slot"],
                    time_range=s["time_range"],
                    title=s["title"],
                    neighborhood=s["neighborhood"],
                    description=s["description"],
                    transit_tip=s["transit_tip"],
                    cost_local=c_loc,
                    cost_usd=c_usd,
                    cost_inr=c_inr,
                    tags=s["tags"],
                    booking_required=s["booking_required"]
                )
                processed_slots.append(act)
                day_local += c_loc

            day_usd = round(day_local / usd_rate, 2)
            day_inr = round(day_usd * inr_rate, 2)
            total_local += day_local

            days_list.append(DayPlan(
                day_number=day_num,
                date_str=cur_date.strftime("%Y-%m-%d"),
                theme=theme,
                neighborhood_cluster=cluster,
                transit_summary=f"Clustered entirely in {cluster} to save 90+ minutes of daily transit.",
                slots=processed_slots,
                daily_cost_local=round(day_local, 2),
                daily_cost_usd=day_usd,
                daily_cost_inr=day_inr
            ))

        total_usd = round(total_local / usd_rate, 2)
        total_inr = round(total_usd * inr_rate, 2)
        end_date_str = (start_dt + timedelta(days=duration_days - 1)).strftime("%Y-%m-%d")

        emergency = EmergencyInfo(
            police_number=meta.get("police", "112"),
            ambulance_number=meta.get("ambulance", "112"),
            tourist_helpline="Available 24/7 at all transit hubs",
            embassy_note=f"Emergency consular services in {meta.get('country', 'capital')}.",
            local_hospital=meta.get("hospital", "General International Hospital"),
            emergency_phrases=["Please help: Assistance", "I need a doctor: J'ai besoin d'un medecin / Ishi"]
        )

        return Itinerary(
            trip_title=f"Signature Odyssey: {destination}",
            destination=destination,
            country=meta.get("country", "International"),
            local_currency_code=curr_code,
            local_currency_symbol=symbol,
            usd_exchange_rate=usd_rate,
            inr_exchange_rate=inr_rate,
            duration_days=duration_days,
            start_date=start_date,
            end_date=end_date_str,
            budget_level=budget_level,
            travel_party=travel_party,
            pace=pace,
            interests=interests,
            days=days_list,
            total_cost_local=round(total_local, 2),
            total_cost_usd=total_usd,
            total_cost_inr=total_inr,
            target_budget_usd=duration_days * (BUDGET_TIERS.get(budget_level, {}).get("max_usd", 150)),
            packing_checklist=[
                "Comfortable broken-in walking shoes",
                "Universal travel plug adapter with USB-C PD",
                "Compact windproof travel umbrella",
                "Crossbody anti-theft sling bag",
                "Portable power bank (10,000 mAh)"
            ],
            cultural_tips=meta.get("cultural_tips", [
                "Greet service staff warmly in the local language.",
                "Always verify restaurant bill inclusions for service charges.",
                "Keep a digital copy of your passport on your phone."
            ]),
            emergency_info=emergency
        )

    def _mock_swap_slot(
        self,
        current_slot: ActivitySlot,
        cluster: str,
        swap_intent: str,
        currency_code: str,
        usd_rate: float,
        inr_rate: float
    ) -> ActivitySlot:
        """Procedural swap for demo mode."""
        intent_lower = swap_intent.lower()
        
        if "veg" in intent_lower or "food" in intent_lower or "lunch" in intent_lower:
            new_title = f"Artisanal Plant-Based & Vegetarian Table ({cluster})"
            new_desc = f"Fresh farm-to-plate organic cuisine and wholesome dishes crafted right in {cluster}. Fully caters to vegetarian and vegan palates."
            new_tags = ["Vegetarian", "Organic Dining", "Healthy"]
            cost_local = current_slot.cost_local * 0.95
        elif "adventure" in intent_lower or "active" in intent_lower:
            new_title = f"Scenic Outdoor Adventure & Viewpoint Trek ({cluster})"
            new_desc = f"An energetic guided outdoor excursion discovering elevated panoramic viewpoints and secret scenic trails around {cluster}."
            new_tags = ["Adventure", "Active", "Panoramic Views"]
            cost_local = current_slot.cost_local * 1.2
        elif "market" in intent_lower or "shop" in intent_lower:
            new_title = f"Vibrant Open-Air Artisan Market ({cluster})"
            new_desc = f"Stroll through bustling neighborhood market stalls featuring handmade textiles, vintage souvenirs, and freshly brewed coffee in {cluster}."
            new_tags = ["Local Market", "Shopping", "Street Vibe"]
            cost_local = current_slot.cost_local * 0.8
        else:
            new_title = f"Curated Experience: {swap_intent.title()} ({cluster})"
            new_desc = f"A customized alternative tailored to '{swap_intent}', carefully situated within {cluster} to prevent cross-town transit."
            new_tags = ["Custom Vibe", "Tailored"]
            cost_local = current_slot.cost_local

        cost_usd = round(cost_local / usd_rate, 2) if usd_rate > 0 else cost_local
        cost_inr = round(cost_usd * inr_rate, 2)

        return ActivitySlot(
            slot_id=current_slot.slot_id,
            time_slot=current_slot.time_slot,
            time_range=current_slot.time_range,
            title=new_title,
            neighborhood=cluster,
            description=new_desc,
            transit_tip=f"Walkable location within {cluster} (under 7 mins)",
            cost_local=round(cost_local, 1),
            cost_usd=cost_usd,
            cost_inr=cost_inr,
            tags=new_tags,
            booking_required=False
        )
