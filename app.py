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
    TRAVEL_PARTY_OPTIONS, PACE_OPTIONS, INTEREST_OPTIONS, DESTINATION_METADATA
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

# Seed default demo trip if DB is fresh
def _ensure_initial_seed():
    if "seeded" not in st.session_state:
        svc = LLMService(provider="Demo")
        sample_trip = svc.generate_itinerary(
            destination="Kyoto, Japan",
            duration_days=3,
            start_date="2026-11-01",
            budget_level="Moderate",
            travel_party="Couple / Romantic",
            pace="Moderate (3-4 activities with balanced breaks)",
            interests=["Art, History & Museums", "Food & Culinary Trails"]
        )
        seed_sample_trip_if_empty(sample_trip)
        if "active_itinerary" not in st.session_state:
            st.session_state["active_itinerary"] = sample_trip
        st.session_state["seeded"] = True

_ensure_initial_seed()

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
            st.caption("⚠️ No API key provided. Falling back to Demo mode if not entered.")
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
            st.caption("⚠️ No API key provided. Falling back to Demo mode if not entered.")
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
    default_dest = st.session_state.get("chosen_destination", "Kyoto, Japan")
    destination_input = st.text_input(
        "Destination City & Region",
        value=default_dest,
        placeholder="e.g. Kyoto, Japan or Paris, France or Amalfi Coast, Italy",
        help="Type any city or pick one recommended from Tab 1."
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
        index=1
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
    target_destination = destination_input.strip() if destination_input.strip() else "Kyoto, Japan"
    with st.spinner(f"Clustering geographic zones and crafting day-by-day plan for {target_destination}..."):
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
            st.success(f"✨ Successfully generated zero-backtracking itinerary for {target_destination}!")
        except Exception as e:
            st.error(f"Failed to generate itinerary: {str(e)}")

# =============================================================================
# MAIN UI HEADER & TABS
# =============================================================================
render_hero_banner()

tab1, tab2, tab3, tab4 = st.tabs([
    "🧭 Smart Destination Recommender",
    "🗺 Day-by-Day Optimized Itinerary",
    "⚡ Vibe Customization & Slot Swap",
    "💾 Trip Management & Offline PDF Export"
])

# Tab 1: Smart Destination Recommender
with tab1:
    render_recommender_tab(llm_service)

# Tab 2: Day-by-Day Itinerary Generator
with tab2:
    render_generator_tab(llm_service, st.session_state.get("active_itinerary"))

# Tab 3: Vibe Customization & Activity Swap
with tab3:
    render_customizer_tab(llm_service)

# Tab 4: Trip Management & PDF Export
with tab4:
    render_trip_manager_tab(st.session_state.get("active_itinerary"))
