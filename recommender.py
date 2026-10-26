"""
Tab 1: Smart Destination Recommender.
Helps users without a fixed destination discover their top 3 matching cities based on
mood, budget, season, travel party, and pace with 1-click adoption into the itinerary builder.
"""

import streamlit as st
from typing import List
from config import VIBE_CATEGORIES, BUDGET_TIERS, TRAVEL_PARTY_OPTIONS, PACE_OPTIONS, INTEREST_OPTIONS
from models import DestinationRecommendation
from llm_service import LLMService


def render_recommender_tab(llm_service: LLMService):
    """Renders the Tab 1 Destination Recommender UI."""
    st.markdown("### 🧭 Smart Destination Recommender")
    st.markdown(
        "Unsure where to travel next? Let the AI route optimizer match your mood, budget, "
        "travel party, and preferred pace with curated global destinations."
    )

    with st.container():
        col1, col2, col3 = st.columns([1.2, 1, 1])
        with col1:
            rec_mood = st.selectbox(
                "Travel Mood & Vibe",
                options=VIBE_CATEGORIES,
                index=0,
                help="What feeling or ambiance are you seeking for this journey?"
            )
        with col2:
            rec_season = st.selectbox(
                "Travel Season / Timeframe",
                options=[
                    "Next 30 Days (Spontaneous)",
                    "Spring (Mar - May)",
                    "Summer (Jun - Aug)",
                    "Autumn / Fall (Sep - Nov)",
                    "Winter (Dec - Feb)"
                ],
                index=2
            )
        with col3:
            rec_budget = st.selectbox(
                "Budget Tier",
                options=list(BUDGET_TIERS.keys()),
                index=1,
                help="Budget level per traveler"
            )

        col4, col5, col6 = st.columns([1.2, 1.2, 1.6])
        with col4:
            rec_party = st.selectbox(
                "Travel Party",
                options=TRAVEL_PARTY_OPTIONS,
                index=0
            )
        with col5:
            rec_pace = st.selectbox(
                "Travel Pace",
                options=PACE_OPTIONS,
                index=1
            )
        with col6:
            rec_interests = st.multiselect(
                "Special Interests & Passions",
                options=INTEREST_OPTIONS,
                default=["Food & Culinary Trails", "Nature & Scenic Landscapes"]
            )

        discover_btn = st.button("✨ Discover Top 3 Matching Destinations", type="primary", use_container_width=True)

    # State storage for recommendations
    if "recommendations_list" not in st.session_state:
        st.session_state["recommendations_list"] = []

    if discover_btn:
        with st.spinner("Analyzing global weather models, flight connectivity, party dynamics, and curated vibe vectors..."):
            try:
                results = llm_service.recommend_destinations(
                    mood=rec_mood,
                    budget=rec_budget,
                    season=rec_season,
                    party=rec_party,
                    interests=rec_interests,
                    pace=rec_pace
                )
                st.session_state["recommendations_list"] = results
                st.session_state["last_rec_search"] = f"{rec_mood} • {rec_party} • {rec_pace} • {rec_budget}"
                st.success(f"Discovered top 3 personalized matches for {rec_mood} ({rec_party})!")
                if llm_service.last_error:
                    st.info(f"ℹ️ Curated with comprehensive destination intelligence engine.")
            except Exception as e:
                st.error(f"Failed to generate recommendations: {str(e)}")

    # Display recommendations
    recs: List[DestinationRecommendation] = st.session_state.get("recommendations_list", [])
    if recs:
        st.markdown("---")
        search_desc = st.session_state.get('last_rec_search', '')
        st.markdown(f"#### 🌟 Curated Top 3 Matches for You {f'({search_desc})' if search_desc else ''}")
        
        cols = st.columns(len(recs))
        for idx, rec in enumerate(recs):
            with cols[idx]:
                with st.container():
                    # Card wrapper
                    st.markdown(
                        f"""
                        <div class="rec-card">
                            <div class="rec-header">
                                <span class="rec-city">{rec.city}</span>
                                <span class="rec-score">★ {rec.match_score}% Match</span>
                            </div>
                            <div style="font-size:0.85rem; color:#64748B; font-weight:600; text-transform:uppercase;">
                                📍 {rec.country} &bull; {rec.vibe_category}
                            </div>
                            <div class="rec-tagline">"{rec.tagline}"</div>
                            <div style="margin-bottom:10px;">
                                <span class="cost-badge">Est. ${rec.estimated_daily_usd:.0f}/day</span>
                                <span class="tag-chip" style="margin-left:6px;">⛅ {rec.best_season}</span>
                            </div>
                            <div style="font-size:0.85rem; color:#334155; margin-bottom:8px;">
                                <b>Why it matches you:</b> {rec.why_you_will_love_it}
                            </div>
                            <div style="font-size:0.82rem; color:#475569; margin-bottom:6px;">
                                <b>Highlights:</b>
                                <ul style="margin:4px 0 8px 18px; padding:0;">
                                    {"".join([f"<li>{h}</li>" for h in rec.top_highlights[:3]])}
                                </ul>
                            </div>
                            <div style="font-size:0.78rem; color:#0284C7; background:#F0F9FF; padding:5px 8px; border-radius:6px; margin-bottom:12px;">
                                🛫 {rec.transit_connectivity}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # 1-Click Action to adopt destination
                    button_key = f"adopt_dest_{idx}_{rec.city.replace(' ', '_').replace('&', '_')}"
                    if st.button(
                        f"🎯 Plan {rec.city} Trip Now",
                        key=button_key,
                        type="primary",
                        use_container_width=True
                    ):
                        dest_str = f"{rec.city}, {rec.country}"
                        st.session_state["chosen_destination"] = dest_str
                        st.session_state["destination_input_value"] = dest_str
                        st.session_state["current_nav_tab"] = "🗺 Day-by-Day Optimized Itinerary"
                        st.session_state["auto_trigger_plan"] = True
                        st.success(f"Selected {rec.city}! Generating customized itinerary...")
                        st.rerun()
    else:
        # Initial empty state prompt
        st.markdown(
            """
            <div style="text-align: center; padding: 40px 20px; background: #FFFFFF; border-radius: 12px; border: 1px dashed #CBD5E1; margin-top: 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">✨</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">Discover Your Next Adventure</div>
                <div style="font-size: 0.9rem; color: #64748B; max-width: 500px; margin: 6px auto 0 auto;">
                    Select your preferred travel mood, party, pace, and budget above. Our AI travel architect will match you with 
                    handpicked destinations with flight accessibility and cost projections.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
