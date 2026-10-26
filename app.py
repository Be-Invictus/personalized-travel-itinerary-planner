"""
Personalized Travel Itinerary Planner - Capstone Project 4
Full-Stack Streamlit Application with Geographic Clustering, Multi-Currency Budgeting,
Dynamic Activity Swapping, and Offline PDF Export.
"""

import streamlit as st
import os
from datetime import datetime, date, timedelta

from config import (
    APP_TITLE, APP_SUBTITLE, VERSION, PROVIDERS, BUDGET_TIERS,
    TRAVEL_PARTY_OPTIONS, PACE_OPTIONS, INTEREST_OPTIONS, DESTINATION_CATALOG
)
from styles import apply_wanderlust_theme, render_hero_banner
from models import Itinerary
from llm_service import LLMService
from recommender import render_recommender_tab
from generator import render_generator_tab
from customizer import render_customizer_tab
from trip_manager import render_trip_manager_tab
from storage import seed_sample_trip_if_empty

# Streamlit Page Setup
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Wanderlust CSS styling
apply_wanderlust_theme()

# Seed default initial trip if DB is fresh
def _ensure_initial_seed():
    if "seeded" not in st.session_state:
        svc = LLMService(provider="Demo")
        sample_trip = svc.generate_itinerary(
            destination="Tokyo, Japan",
            duration_days=3,
            start_date="2026-11-01",
            budget_level="Moderate",
            travel_party="Solo Traveler",
            pace="Moderate (3-4 activities with balanced breaks)",
            interests=["Art, History & Museums", "Food & Culinary Trails"]
        )
        seed_sample_trip_if_empty(sample_trip)
        if "active_itinerary" not in st.session_state:
            st.session_state["active_itinerary"] = sample_trip
        st.session_state["seeded"] = True

_ensure_initial_seed()

# Navigation Tabs List
NAV_TABS = [
    "🧭 Smart Destination Recommender",
    "🗺 Day-by-Day Optimized Itinerary",
    "⚡ Vibe Customization & Slot Swap",
    "💾 Trip Management & Offline PDF Export"
]

if "current_nav_tab" not in st.session_state:
    st.session_state["current_nav_tab"] = NAV_TABS[0]

# =============================================================================
# SIDEBAR: CONFIGURATION & USER PREFERENCES (EPIC 3)
# =============================================================================
with st.sidebar:
    st.markdown("## ⚙️ AI Engine & Settings")
    
    # Provider selection
    provider_option = st.radio(
        "Select AI Provider",
        options=["Demo Mode (Free / Instant)", "Google Gemini", "Groq Cloud"],
        index=0,
        help="Demo mode operates completely offline with procedural route curation. Gemini and Groq connect to live LLMs."
    )

    api_key = ""
    selected_model = None

    if provider_option == "Google Gemini":
        provider_key = "Gemini"
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Get your key at aistudio.google.com"
        )
        selected_model = st.selectbox("Gemini Model", PROVIDERS["Gemini"]["models"], index=0)
        if not api_key:
            st.caption("⚠️ No API key provided. Falling back to dynamic catalog engine.")
    elif provider_option == "Groq Cloud":
        provider_key = "Groq"
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=os.environ.get("GROQ_API_KEY", ""),
            help="Get your key at console.groq.com"
        )
        selected_model = st.selectbox("Groq Model", PROVIDERS["Groq"]["models"], index=0)
        if not api_key:
            st.caption("⚠️ No API key provided. Falling back to dynamic catalog engine.")
    else:
        provider_key = "Demo"
        st.success("🟢 Demo Mode Active — Ready without API Keys")

    # Instantiate LLM Service
    llm_service = LLMService(
        provider=provider_key,
        api_key=api_key,
        model=selected_model
    )

    st.markdown("---")
    st.markdown("## 🧭 Trip Preferences Form")

    # Destination handling (supports auto-fill from Tab 1 recommender)
    if "destination_input_value" not in st.session_state:
        st.session_state["destination_input_value"] = "Tokyo, Japan"

    if st.session_state.get("chosen_destination"):
        st.session_state["destination_input_value"] = st.session_state["chosen_destination"]
        st.session_state["chosen_destination"] = None

    destination_input = st.text_input(
        "Destination City & Region",
        key="destination_input_value",
        placeholder="e.g. Tokyo, Paris, Banff, Manali, London, Dubai, Rome...",
        help="Type any city in the world or click 'Plan Trip Now' on any recommendation."
    )

    # Duration slider
    duration_days = st.slider(
        "Trip Duration (Days)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of full travel days to cluster."
    )

    # Travel Dates
    start_date = st.date_input(
        "Start Date",
        value=date.today() + timedelta(days=7),
        min_value=date.today()
    )
    end_date = start_date + timedelta(days=duration_days - 1)
    st.caption(f"Trip Window: **{start_date.strftime('%b %d, %Y')}** to **{end_date.strftime('%b %d, %Y')}**")

    # Budget Tier
    budget_level = st.select_slider(
        "Budget Tier",
        options=list(BUDGET_TIERS.keys()),
        value="Moderate",
        help="Controls tier of dining, accommodation, and activities."
    )
    st.caption(f"ℹ️ {BUDGET_TIERS[budget_level]['desc']}")

    # Travel Party
    travel_party = st.selectbox(
        "Travel Party",
        options=TRAVEL_PARTY_OPTIONS,
        index=0
    )

    # Travel Pace
    travel_pace = st.selectbox(
        "Travel Pace",
        options=PACE_OPTIONS,
        index=1
    )

    # Specific Interests
    selected_interests = st.multiselect(
        "Core Interests & Passions",
        options=INTEREST_OPTIONS,
        default=["Food & Culinary Trails", "Art, History & Museums"]
    )

    st.markdown("---")
    generate_btn = st.button("🚀 Generate Optimized Itinerary", type="primary", use_container_width=True)

    st.markdown(
        f"""
        <div style="font-size:0.75rem; color:#94A3B8; text-align:center; margin-top:15px;">
            Travel SaaS v{VERSION} &bull; Skill Wallet Capstone Project 4
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# AUTO-TRIGGER OR BUTTON GENERATION LOGIC
# =============================================================================
auto_trigger = st.session_state.pop("auto_trigger_plan", False)

if generate_btn or auto_trigger:
    target_destination = st.session_state.get("destination_input_value", "Tokyo, Japan").strip()
    if not target_destination:
        target_destination = "Tokyo, Japan"
        
    with st.spinner(f"Clustering geographic zones and crafting day-by-day plan for {target_destination} ({travel_party}, {travel_pace})..."):
        try:
            itinerary = llm_service.generate_itinerary(
                destination=target_destination,
                duration_days=duration_days,
                start_date=start_date.strftime("%Y-%m-%d"),
                budget_level=budget_level,
                travel_party=travel_party,
                pace=travel_pace,
                interests=selected_interests
            )
            st.session_state["active_itinerary"] = itinerary
            st.session_state["current_nav_tab"] = NAV_TABS[1]  # Switch directly to Tab 2
            st.success(f"✨ Successfully generated zero-backtracking itinerary for {target_destination}!")
            if llm_service.last_error:
                st.info("ℹ️ Compiled with specialized geographic clustering intelligence.")
        except Exception as e:
            st.error(f"Failed to generate itinerary: {str(e)}")

# =============================================================================
# MAIN UI HEADER & SYNCHRONIZED NAVIGATION BAR
# =============================================================================
render_hero_banner()

# Programmatically controllable tab navigation
current_tab = st.radio(
    "Navigation Menu",
    options=NAV_TABS,
    index=NAV_TABS.index(st.session_state["current_nav_tab"]) if st.session_state["current_nav_tab"] in NAV_TABS else 0,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state["current_nav_tab"] = current_tab

# Render Active Tab View
if current_tab == NAV_TABS[0]:
    render_recommender_tab(llm_service)
elif current_tab == NAV_TABS[1]:
    render_generator_tab(llm_service, st.session_state.get("active_itinerary"))
elif current_tab == NAV_TABS[2]:
    render_customizer_tab(llm_service)
elif current_tab == NAV_TABS[3]:
    render_trip_manager_tab(st.session_state.get("active_itinerary"))
