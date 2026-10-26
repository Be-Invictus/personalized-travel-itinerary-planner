"""
LLM Service Layer: Handles Gemini, Groq, structured JSON output, prompt engineering,
and resilient dynamic recommendation and itinerary generation.
"""

import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from config import CURRENCIES, DESTINATION_CATALOG, DESTINATION_METADATA, BUDGET_TIERS
from models import (
    Itinerary, DayPlan, ActivitySlot, DestinationRecommendation, EmergencyInfo
)


def _clean_json_string(raw_str: str) -> str:
    """Extracts clean JSON from raw LLM output even if surrounded by markdown or commentary."""
    text = raw_str.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    else:
        first_bracket = min((text.find('{'), text.find('[')))
        if first_bracket != -1:
            last_bracket = max((text.rfind('}'), text.rfind(']')))
            if last_bracket > first_bracket:
                text = text[first_bracket:last_bracket + 1]
    
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def _find_catalog_destination(dest_query: str) -> Optional[Dict[str, Any]]:
    """Finds a catalog entry by city name; country alone is not a city match."""
    q = re.sub(r"[^a-z0-9]+", " ", dest_query.lower()).strip()
    matches = []
    for item in DESTINATION_CATALOG:
        city_name = item["city"].lower()
        city_aliases = [city_name]
        if "&" in city_name:
            city_aliases.extend(part.strip() for part in city_name.split("&"))
        for alias in city_aliases:
            normalized_alias = re.sub(r"[^a-z0-9]+", " ", alias).strip()
            if normalized_alias and re.search(rf"\b{re.escape(normalized_alias)}\b", q):
                matches.append((len(normalized_alias), item))
                break
    return max(matches, key=lambda match: match[0])[1] if matches else None


def _find_catalog_country(country_query: str) -> Optional[Dict[str, Any]]:
    """Finds currency/country defaults without treating the country as its first city."""
    normalized_query = re.sub(r"[^a-z0-9]+", " ", country_query.lower()).strip()
    return next(
        (
            item for item in DESTINATION_CATALOG
            if re.sub(r"[^a-z0-9]+", " ", item["country"].lower()).strip() == normalized_query
        ),
        None,
    )


def _format_destination(destination: str, country_name: str) -> str:
    """Formats freeform destinations consistently for the itinerary display."""
    city_name = destination.split(",", 1)[0].strip().title()
    if country_name == "International":
        return city_name
    return f"{city_name}, {country_name}"


class LLMService:
    """Unified AI service supporting Google Gemini, Groq, and intelligent dynamic Demo Mode."""

    def __init__(self, provider: str = "Demo", api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY") or ""
        self.model = model
        self.is_demo = (provider == "Demo" or not self.api_key.strip())
        self.last_error: Optional[str] = None

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Invokes Google Gemini with fallback between google-genai and google.generativeai."""
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
            raise ValueError("Demo mode active; using procedural route engine.")
        
        if self.provider == "Gemini":
            return self._call_gemini(prompt, system_instruction)
        elif self.provider == "Groq":
            return self._call_groq(prompt, system_instruction)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # =========================================================================
    # TAB 1: DESTINATION RECOMMENDATIONS (DYNAMIC & USER-TAILORED)
    # =========================================================================

    def recommend_destinations(
        self,
        mood: str,
        budget: str,
        season: str,
        party: str,
        interests: List[str],
        pace: str = "Moderate"
    ) -> List[DestinationRecommendation]:
        """Generates 3 matching destination recommendations dynamically based on user preferences."""
        if self.is_demo:
            return self._mock_recommendations(mood, budget, season, party, pace, interests)

        system_instruction = (
            "You are a master travel curator. Recommend exactly 3 distinct destinations matching the user's "
            "vibe, budget tier, season, party type, pace, and interests. Return strictly valid JSON array of objects."
        )

        prompt = f"""
        Recommend 3 extraordinary travel destinations based on:
        - Travel Mood / Vibe: {mood}
        - Budget Tier: {budget}
        - Travel Season / Month: {season}
        - Travel Party: {party}
        - Travel Pace: {pace}
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
            "why_you_will_love_it": "Why this specifically suits a {party} at a {pace} pace and {budget} budget."
          }}
        ]
        """
        try:
            raw_output = self.generate_raw(prompt, system_instruction)
            cleaned = _clean_json_string(raw_output)
            data = json.loads(cleaned)
            if isinstance(data, dict):
                for k in ["destinations", "recommendations", "cities", "results"]:
                    if k in data and isinstance(data[k], list):
                        data = data[k]
                        break
            if isinstance(data, list):
                return [DestinationRecommendation(**item) for item in data[:3]]
            raise ValueError("Invalid JSON schema received from LLM")
        except Exception as e:
            self.last_error = str(e)
            # Resilient fallback to dynamically scored catalog
            return self._mock_recommendations(mood, budget, season, party, pace, interests)

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

        cat_dest = _find_catalog_destination(destination)
        country_input = destination.split(",")[-1].strip() if "," in destination else ""
        country_defaults = _find_catalog_country(country_input) if country_input else None
        destination_metadata = cat_dest or country_defaults
        country_name = (
            cat_dest["country"] if cat_dest else
            country_input.title() if country_input else "International"
        )
        display_destination = _format_destination(destination, country_name)
        curr_code = destination_metadata.get("currency", "USD") if destination_metadata else "USD"
        curr_info = CURRENCIES.get(curr_code, CURRENCIES["USD"])
        usd_rate = curr_info["rate_from_usd"]
        inr_rate = CURRENCIES["INR"]["rate_from_usd"]
        symbol = curr_info["symbol"]

        system_instruction = (
            "You are a senior full-stack travel SaaS architect and master geographic route optimizer. "
            "Your critical rule is GEOGRAPHIC CLUSTERING: every single day must strictly cluster attractions, "
            "restaurants, and activities within ONE specific geographic neighborhood/district to eliminate cross-city "
            "backtracking and minimize transit fatigue. Tailor activities specifically to the travel party and pace. Return strictly valid JSON."
        )

        prompt = f"""
        Create a detailed {duration_days}-day itinerary for {destination}.
        Trip Parameters:
        - Start Date: {start_date}
        - Budget Level: {budget_level}
        - Travel Party: {travel_party} (IMPORTANT: Customize activities, dining, and transit specifically for {travel_party}!)
        - Travel Pace: {pace} (IMPORTANT: Calibrate daily activity count and rest periods to match {pace}!)
        - Specific Interests: {', '.join(interests) if interests else 'Culture, Food, Sights'}
        - Local Currency: {curr_code} ({symbol}), Rate: 1 USD = {usd_rate} {curr_code}

        CRITICAL INSTRUCTIONS:
        1. Each day MUST focus on a distinct neighborhood / zone of {destination} (e.g. Historic Quarter, Waterfront, Arts District).
        2. Sequence each day with 4 slots: 'Morning', 'Lunch', 'Afternoon', 'Evening'.
        3. All 4 slots for that day MUST be located within or adjacent to that day's neighborhood cluster.
        4. State the walking/transit recommendation in each slot (e.g. '5-min walk down Royal Street' or 'Short 2-stop tram #4').
        5. Provide realistic itemized estimated costs per slot in local currency ({curr_code}) matching the {budget_level} budget tier.

        Return ONLY a JSON object with this exact schema:
        {{
          "trip_title": "Signature Journey: {destination}",
          "destination": "{destination}",
          "country": "{country_name}",
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
                  "description": "Engaging activity details tailored to {travel_party}",
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
                  "title": "Evening dining and atmosphere",
                  "neighborhood": "Cluster district",
                  "description": "Dinner venue and evening promenade tailored to {travel_party}",
                  "transit_tip": "Walk within cluster",
                  "cost_local": 40.0,
                  "cost_usd": 40.0,
                  "cost_inr": 3400.0,
                  "tags": ["Dining", "Atmosphere"],
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
            "emergency_phrases": ["Help!", "Where is the hospital?"]
          }}
        }}
        """

        try:
            raw_output = self.generate_raw(prompt, system_instruction)
            cleaned = _clean_json_string(raw_output)
            data = json.loads(cleaned)
            data["trip_title"] = f"Signature Journey: {display_destination}"
            data["destination"] = display_destination
            data["country"] = country_name
            data["local_currency_code"] = curr_code
            data["local_currency_symbol"] = symbol
            itinerary = self._process_itinerary_costs(data, usd_rate, inr_rate)
            return itinerary
        except Exception as e:
            self.last_error = str(e)
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
    # DYNAMIC SCORING RECOMMENDATIONS ENGINE (SOLVES THE ALWAYS KYOTO BUG)
    # =========================================================================

    def _mock_recommendations(
        self,
        mood: str,
        budget: str,
        season: str,
        party: str,
        pace: str,
        interests: List[str]
    ) -> List[DestinationRecommendation]:
        """
        Dynamically scores and ranks all destinations in DESTINATION_CATALOG based on
        the user's EXACT mood, budget, season, party, pace, and interests.
        Guarantees distinct, tailored top 3 options rather than static repeats.
        """
        scored_candidates = []

        for dest in DESTINATION_CATALOG:
            score = 50  # Base score

            # 1. Vibe matching: Higher weight if primary vibe (+45), secondary (+35)
            if dest.get("vibes") and dest["vibes"][0] == mood:
                score += 45
            elif mood in dest.get("vibes", []):
                score += 35
            elif any(v.split()[0].lower() in mood.lower() for v in dest.get("vibes", [])):
                score += 15

            # 2. Budget compatibility (+20)
            if budget in dest.get("budgets", []):
                score += 20

            # 3. Travel party compatibility (+20)
            if party in dest.get("parties", []):
                score += 20
            elif "Family" in party and "Family with Kids" in dest.get("parties", []):
                score += 20
            elif "Solo" in party and "Solo Traveler" in dest.get("parties", []):
                score += 20

            # 4. Travel pace compatibility (+10)
            pace_key = pace.split()[0]  # Relaxed, Moderate, Fast-Paced
            if any(pace_key in p for p in dest.get("paces", [])):
                score += 10

            # 5. Season alignment (+10)
            season_key = season.split()[0]  # Summer, Spring, Winter, Autumn
            if any(season_key in s for s in dest.get("seasons", [])):
                score += 10

            # 6. Specific user interests bonus (+5 per match, up to +15)
            if interests:
                match_count = 0
                dest_text = (dest.get("tagline", "") + " " + " ".join(dest.get("highlights", [])) + " " + dest.get("why", "")).lower()
                for interest in interests:
                    keywords = [w.lower() for w in interest.split() if len(w) > 3 and w.lower() not in ["and", "with"]]
                    if any(kw in dest_text for kw in keywords):
                        match_count += 1
                score += min(15, match_count * 5)

            scored_candidates.append((score, dest))

        # Sort descending by raw compatibility score FIRST before formatting
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_3 = scored_candidates[:3]

        recommendations = []
        for rank, (raw_score, dest) in enumerate(top_3):
            # Display match score cleanly scaled: 98% for rank 0, 96% for rank 1, 94% for rank 2
            display_score = 98 - (rank * 2)

            # Custom personalized explanation matching user's specific party and pace
            party_label = party.split()[0].lower()
            pace_label = pace.split()[0].lower()
            personalized_why = (
                f"{dest['why']} Perfectly suited for a {party_label} traveling at a {pace_label} pace "
                f"within a {budget.lower()} budget framework."
            )

            # Adjust daily budget based on user budget tier
            base_usd = dest.get("daily_usd", 150.0)
            if budget == "Budget":
                adjusted_usd = round(base_usd * 0.55, 0)
            elif budget == "Luxury":
                adjusted_usd = round(base_usd * 2.2, 0)
            else:
                adjusted_usd = round(base_usd, 0)

            recommendations.append(
                DestinationRecommendation(
                    city=dest["city"],
                    country=dest["country"],
                    tagline=dest["tagline"],
                    match_score=display_score,
                    vibe_category=mood,
                    best_season=dest.get("seasons", ["Year-round"])[0],
                    estimated_daily_usd=adjusted_usd,
                    top_highlights=dest.get("highlights", ["Historic Center", "Local Cuisine", "Scenic Vista"]),
                    transit_connectivity=dest.get("connectivity", "International airport with direct flights"),
                    why_you_will_love_it=personalized_why
                )
            )

        return recommendations

    # =========================================================================
    # DYNAMIC ITINERARY PROCEDURAL ENGINE TAILORED TO PARTY, PACE & CITY
    # =========================================================================

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
        """
        Generates an authentic, geographically clustered itinerary dynamically tailored to:
        - The specific destination (matched from catalog or dynamically extrapolated)
        - Travel party (Solo, Couple, Family with Kids, Friends)
        - Travel pace (Relaxed vs Moderate vs Fast-Paced)
        """
        cat = _find_catalog_destination(destination)
        country_input = destination.split(",")[-1].strip() if "," in destination else ""
        country_defaults = _find_catalog_country(country_input) if country_input else None

        if cat:
            city_display = cat["city"]
            country_name = cat["country"]
            destination = _format_destination(destination, country_name)
            curr_code = cat.get("currency", "USD")
            curr_info = CURRENCIES.get(curr_code, CURRENCIES["USD"])
            usd_rate = curr_info["rate_from_usd"]
            inr_rate = CURRENCIES["INR"]["rate_from_usd"]
            symbol = curr_info["symbol"]
            clusters = cat.get("clusters", [f"{city_display} Central Quarter", f"{city_display} Waterfront", f"{city_display} Arts Quarter"])
            highlights = cat.get("highlights", [f"{city_display} Historic Center", f"{city_display} Viewpoint"])
            cultural_tips = cat.get("cultural_tips", ["Keep local currency on hand", "Respect sacred cultural sites", "Tipping practices vary"])
        else:
            # Custom / Freeform City parsed dynamically
            clean_city = destination.split(",")[0].strip()
            city_display = clean_city.title()
            country_name = country_input.title() if country_input else "International"
            destination = _format_destination(destination, country_name)
            curr_code = country_defaults.get("currency", "USD") if country_defaults else "USD"
            curr_info = CURRENCIES.get(curr_code, CURRENCIES["USD"])
            usd_rate = curr_info["rate_from_usd"]
            inr_rate = CURRENCIES["INR"]["rate_from_usd"]
            symbol = curr_info["symbol"]
            clusters = [
                f"{city_display} Historic Old Town & Central Plaza",
                f"{city_display} Arts Quarter & Waterfront Promenade",
                f"{city_display} Hillside Ridge & Panoramic Viewpoints",
                f"{city_display} Culinary District & Open-Air Markets"
            ]
            highlights = [
                f"{city_display} Ancient Historic Center",
                f"{city_display} River/Waterfront Promenade",
                f"{city_display} Local Artisan Bazaar",
                f"{city_display} Panoramic Sunset Point"
            ]
            cultural_tips = [
                f"Respect local photography customs around sacred monuments in {city_display}.",
                "Carry local currency cash for authentic neighborhood street vendors.",
                "Comfortable walking footwear is essential for cobblestone historic districts."
            ]

        # Party-specific adaptations
        is_family = "Family" in travel_party
        is_solo = "Solo" in travel_party
        is_romantic = "Couple" in travel_party or "Romantic" in travel_party
        is_friends = "Friends" in travel_party

        # Pace-specific adaptations
        is_relaxed = "Relaxed" in pace
        is_fast = "Fast" in pace

        # Time ranges based on pace
        if is_relaxed:
            t_morning = "10:00 - 12:30"
            t_lunch = "13:00 - 14:45"
            t_afternoon = "15:30 - 17:30"
            t_evening = "18:30 - 21:00"
        elif is_fast:
            t_morning = "08:30 - 11:30"
            t_lunch = "12:00 - 13:30"
            t_afternoon = "14:00 - 17:30"
            t_evening = "18:30 - 23:00"
        else:
            t_morning = "09:00 - 12:00"
            t_lunch = "12:30 - 14:00"
            t_afternoon = "14:30 - 17:30"
            t_evening = "18:30 - 22:00"

        # Budget multipliers
        multiplier = 0.6 if budget_level == "Budget" else (1.0 if budget_level == "Moderate" else 2.5)

        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        days_list = []
        total_local = 0.0

        for day_idx in range(duration_days):
            day_num = day_idx + 1
            cur_date = start_dt + timedelta(days=day_idx)
            cluster = clusters[day_idx % len(clusters)]

            # Curated day themes
            themes = [
                f"{cluster} Architectural Anchors & Living Heritage",
                f"{cluster} Artisan Alleys & Regional Flavors",
                f"{cluster} Panoramic Horizons & Scenic Trails",
                f"{cluster} Riverside Promenades & Vibrant Evening Markets"
            ]
            theme = themes[day_idx % len(themes)]

            # Party-tailored titles and descriptions
            if is_family:
                m_title = f"Interactive Landmark Discovery in {cluster}"
                m_desc = f"Family-friendly morning exploration of {cluster}. Spacious walking trails, interactive exhibits for all ages, and minimal waiting times."
                l_title = f"Relaxed Family Table at {cluster} Bistro"
                l_desc = f"Wholesome regional lunch with kid-friendly menu selections, high chairs, and spacious seating in {cluster}."
                a_title = f"Parks, Gardens & Sweet Treats in {cluster}"
                a_desc = f"Leisurely stroll through tranquil gardens or open plazas in {cluster} with gelato/bakery stop and play spaces."
                e_title = f"Early Dinner & Ambient Evening Stroll in {cluster}"
                e_desc = f"Cozy early evening dinner close to transit hubs, designed to avoid overtiring young travelers."
            elif is_romantic:
                m_title = f"Scenic Morning Stroll & Heritage Sights in {cluster}"
                m_desc = f"Hand-in-hand morning walk through the romantic cobblestone alleys and picturesque viewpoints of {cluster}."
                l_title = f"Charming Courtyard Lunch & Wine in {cluster}"
                l_desc = f"Intimate table tucked into a quiet lane of {cluster}, featuring regional wine pairings and artisanal dishes."
                a_title = f"Artisan Boutiques & Secret Viewpoints in {cluster}"
                a_desc = f"Discover hidden cloistered courtyards, boutique perfumeries/crafts, and quiet lookout points in {cluster}."
                e_title = f"Candlelit Sunset Dinner & Promenade in {cluster}"
                e_desc = f"Panoramic sunset dining with breathtaking vistas, followed by an illuminated evening walk through {cluster}."
            elif is_solo:
                m_title = f"Self-Guided Walking Route & Iconic Sights in {cluster}"
                m_desc = f"Empowering solo exploration of {cluster}. Highly walkable, safe, and packed with photo opportunities and local history."
                l_title = f"Artisan Coffee & Communal Lunch Table in {cluster}"
                l_desc = f"Vibrant, solo-traveler friendly cafe featuring counter seating, exceptional local dishes, and fast Wi-Fi."
                a_title = f"Independent Museums & Neighborhood Vibe in {cluster}"
                a_desc = f"Explore curated local galleries and tranquil reading courtyards at your own relaxed pace in {cluster}."
                e_title = f"Social Food Market Crawl & Craft Beverages in {cluster}"
                e_desc = f"Engage with fellow travelers and locals at an energetic food market and casual acoustic lounge in {cluster}."
            else:  # Friends / General
                m_title = f"Must-See Highlights & Group Photos in {cluster}"
                m_desc = f"Kick off the morning with the most iconic photo viewpoints and celebrated monuments clustered in {cluster}."
                l_title = f"Bustling Tapas / Street-Style Feast in {cluster}"
                l_desc = f"Energetic group dining with shareable platters, local specialties, and vibrant social ambiance in {cluster}."
                a_title = f"Open-Air Market & Active Walkway in {cluster}"
                a_desc = f"Stroll through buzzing local artisan stalls, vintage flea markets, and scenic pedestrian paths in {cluster}."
                e_title = f"Rooftop Sunset Drinks & Nightlife in {cluster}"
                e_desc = f"Toast to Day {day_num} from a scenic rooftop terrace, followed by dinner and energetic nightlife in {cluster}."

            base_slots = [
                {
                    "slot_id": f"day{day_num}_morning",
                    "time_slot": "Morning",
                    "time_range": t_morning,
                    "title": m_title,
                    "neighborhood": cluster,
                    "description": m_desc,
                    "transit_tip": f"Take the local metro/bus to {cluster} Central Hub; short 3-min walk.",
                    "cost_local": round(15.0 * usd_rate * multiplier, 1),
                    "tags": ["Culture", "Landmark", travel_party.split()[0]],
                    "booking_required": True if budget_level == "Luxury" else False
                },
                {
                    "slot_id": f"day{day_num}_lunch",
                    "time_slot": "Lunch",
                    "time_range": t_lunch,
                    "title": l_title,
                    "neighborhood": cluster,
                    "description": l_desc,
                    "transit_tip": f"Short scenic 4-minute walk from morning activity within {cluster}.",
                    "cost_local": round(20.0 * usd_rate * multiplier, 1),
                    "tags": ["Culinary", "Local Gastronomy"],
                    "booking_required": False
                },
                {
                    "slot_id": f"day{day_num}_afternoon",
                    "time_slot": "Afternoon",
                    "time_range": t_afternoon,
                    "title": a_title,
                    "neighborhood": cluster,
                    "description": a_desc,
                    "transit_tip": f"Zero transit transfers needed; all stops within 350m radius in {cluster}.",
                    "cost_local": round(12.0 * usd_rate * multiplier, 1),
                    "tags": ["Scenic", "Leisure", pace.split()[0]],
                    "booking_required": False
                },
                {
                    "slot_id": f"day{day_num}_evening",
                    "time_slot": "Evening",
                    "time_range": t_evening,
                    "title": e_title,
                    "neighborhood": cluster,
                    "description": e_desc,
                    "transit_tip": f"Short stroll within {cluster}; convenient taxi/rideshare stand nearby.",
                    "cost_local": round(35.0 * usd_rate * multiplier, 1),
                    "tags": ["Dining", "Atmosphere"],
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
                transit_summary=f"Clustered entirely in {cluster} to eliminate cross-city transit fatigue for a {travel_party.lower()}.",
                slots=processed_slots,
                daily_cost_local=round(day_local, 2),
                daily_cost_usd=day_usd,
                daily_cost_inr=day_inr
            ))

        total_usd = round(total_local / usd_rate, 2)
        total_inr = round(total_usd * inr_rate, 2)
        end_date_str = (start_dt + timedelta(days=duration_days - 1)).strftime("%Y-%m-%d")

        emergency = EmergencyInfo(
            police_number="112" if country_name in ["France", "Spain", "Italy", "Greece", "India"] else "911",
            ambulance_number="112",
            tourist_helpline=f"Available 24/7 at {city_display} central tourist information office",
            embassy_note=f"Emergency consular services available in {country_name}.",
            local_hospital=f"{city_display} Central International Medical Center",
            emergency_phrases=["Please help / Urgent assistance required", "Where is the nearest medical clinic?"]
        )

        return Itinerary(
            trip_title=f"Curated Odyssey: {destination}",
            destination=destination,
            country=country_name,
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
            cultural_tips=cultural_tips,
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
