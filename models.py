"""
Pydantic Data Models for Personalized Travel Itinerary Planner.
Provides strong typing, validation, and JSON serialization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ActivitySlot(BaseModel):
    """Represents a single scheduled activity in a day."""
    slot_id: str = Field(description="Unique identifier for the slot (e.g. 'day1_morning')")
    time_slot: str = Field(description="Time slot label (Morning, Lunch, Afternoon, Evening)")
    time_range: str = Field(description="Formatted time range (e.g. '09:00 - 12:00')")
    title: str = Field(description="Title of the activity or venue")
    neighborhood: str = Field(description="Neighborhood, district, or geographic cluster")
    description: str = Field(description="Detailed description of what to see or do")
    transit_tip: str = Field(description="Walking or public transit recommendation from previous activity")
    cost_local: float = Field(default=0.0, description="Estimated cost in local destination currency")
    cost_usd: float = Field(default=0.0, description="Estimated cost converted to USD")
    cost_inr: float = Field(default=0.0, description="Estimated cost converted to INR")
    tags: List[str] = Field(default_factory=list, description="Category tags like 'Culture', 'Scenic', 'Vegetarian Friendly'")
    booking_required: bool = Field(default=False, description="Whether advance reservations or tickets are recommended")


class DayPlan(BaseModel):
    """Represents the complete schedule for one travel day."""
    day_number: int = Field(description="Day number (1, 2, 3...)")
    date_str: str = Field(description="Date formatted as string, e.g. '2026-11-01'")
    theme: str = Field(description="Curated daily theme (e.g. 'Historic Temples & Zen Gardens')")
    neighborhood_cluster: str = Field(description="Primary geographic area or district clustered for this day")
    transit_summary: str = Field(description="Summary of transit strategy to minimize backtracking")
    slots: List[ActivitySlot] = Field(description="The 4 sequential time slots for the day")
    daily_cost_local: float = Field(default=0.0, description="Total estimated cost for the day in local currency")
    daily_cost_usd: float = Field(default=0.0, description="Total estimated cost for the day in USD")
    daily_cost_inr: float = Field(default=0.0, description="Total estimated cost for the day in INR")


class DestinationRecommendation(BaseModel):
    """Represents an AI-generated destination recommendation."""
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    tagline: str = Field(description="Captivating 1-sentence tagline")
    match_score: int = Field(default=95, description="Compatibility score percentage (e.g. 96)")
    vibe_category: str = Field(description="Vibe category (e.g. Cultural, Beach, Mountain, Urban)")
    best_season: str = Field(description="Recommended months/season to visit")
    estimated_daily_usd: float = Field(description="Estimated daily cost per person in USD")
    top_highlights: List[str] = Field(description="Top 3-4 key attractions or experiences")
    transit_connectivity: str = Field(description="Flight & transit convenience rating (e.g. 'Direct International Flights')")
    why_you_will_love_it: str = Field(description="Personalized rationale matching user preferences")


class EmergencyInfo(BaseModel):
    """Local emergency details for offline readiness."""
    police_number: str = Field(default="112")
    ambulance_number: str = Field(default="112")
    tourist_helpline: str = Field(default="Available at airport and major stations")
    embassy_note: str = Field(default="Locate your national embassy in the capital city.")
    local_hospital: str = Field(default="General Hospital with English-speaking staff")
    emergency_phrases: List[str] = Field(default_factory=list)


class Itinerary(BaseModel):
    """The master itinerary containing all days, meta-info, and budget tracking."""
    trip_title: str = Field(description="Evocative title for the trip")
    destination: str = Field(description="Destination city and region")
    country: str = Field(description="Destination country")
    local_currency_code: str = Field(default="USD", description="Currency code (e.g. JPY, EUR, USD, INR)")
    local_currency_symbol: str = Field(default="$", description="Currency symbol (e.g. ¥, €, $, ₹)")
    usd_exchange_rate: float = Field(default=1.0, description="1 USD = X Local Currency")
    inr_exchange_rate: float = Field(default=85.0, description="1 USD = X INR")
    duration_days: int = Field(description="Total number of travel days")
    start_date: str = Field(description="Trip start date")
    end_date: str = Field(description="Trip end date")
    budget_level: str = Field(description="Budget tier (Budget, Moderate, Luxury)")
    travel_party: str = Field(description="Travel group (Solo, Couple, Family, Friends)")
    pace: str = Field(description="Pace (Relaxed, Moderate, Fast-Paced)")
    interests: List[str] = Field(default_factory=list)
    days: List[DayPlan] = Field(default_factory=list)
    total_cost_local: float = Field(default=0.0)
    total_cost_usd: float = Field(default=0.0)
    total_cost_inr: float = Field(default=0.0)
    target_budget_usd: float = Field(default=0.0)
    packing_checklist: List[str] = Field(default_factory=list)
    cultural_tips: List[str] = Field(default_factory=list)
    emergency_info: Optional[EmergencyInfo] = None


class TripRecord(BaseModel):
    """Record saved in persistent storage."""
    trip_id: str
    created_at: str
    updated_at: str
    trip_title: str
    destination: str
    duration_days: int
    total_cost_usd: float
    itinerary_data: Dict[str, Any]
    user_notes: str = ""
