"""
Tab 2: Day-by-Day Optimized Itinerary Generator.
Implements sequential time slots, strict geographic clustering, and multi-currency budget telemetry.
"""

import streamlit as st
from typing import Optional
from models import Itinerary, DayPlan, ActivitySlot
from llm_service import LLMService
from config import CURRENCIES


def render_generator_tab(llm_service: LLMService, current_itinerary: Optional[Itinerary] = None):
    """Renders the Tab 2 Day-by-Day Itinerary Generator & Visualizer."""
    st.markdown("### 🗺 Day-by-Day Optimized Itinerary Generator")
    st.markdown(
        "Generate a structured, zero-backtracking travel plan. Every day is clustered into a "
        "single neighborhood zone with sequential time slots and live multi-currency budget tracking."
    )

    itinerary = current_itinerary or st.session_state.get("active_itinerary")

    if not itinerary:
        st.info("👈 Configure your trip preferences in the left sidebar and click **'🚀 Generate Optimized Itinerary'** to build your plan!")
        return

    # Currency Display Mode Selector
    curr_col1, curr_col2 = st.columns([2.5, 1.5])
    with curr_col1:
        st.markdown(f"#### ✈ {itinerary.trip_title}")
        st.markdown(
            f"**Destination:** {itinerary.destination}, {itinerary.country} &nbsp;|&nbsp; "
            f"**Dates:** {itinerary.start_date} &bull; {itinerary.duration_days} Days &nbsp;|&nbsp; "
            f"**Party:** {itinerary.travel_party} &bull; {itinerary.pace}"
        )
    with curr_col2:
        currency_view = st.radio(
            "Currency View",
            options=["Dual (Local + USD)", "USD ($)", "Indian Rupee (₹)", "Local Only"],
            horizontal=True,
            index=0
        )

    # =========================================================================
    # MULTI-CURRENCY RUNNING BUDGET TRACKER METRICS
    # =========================================================================
    st.markdown("---")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    total_usd = itinerary.total_cost_usd
    total_inr = itinerary.total_cost_inr
    total_loc = itinerary.total_cost_local
    loc_sym = itinerary.local_currency_symbol
    loc_code = itinerary.local_currency_code
    target_budget = itinerary.target_budget_usd or (itinerary.duration_days * 150)
    budget_variance = target_budget - total_usd

    with m_col1:
        st.markdown(
            f"""
            <div class="metric-pill-box">
                <div class="metric-pill-lbl">Total Estimated Cost</div>
                <div class="metric-pill-val" style="color:#2A9D8F;">${total_usd:,.0f}</div>
                <div style="font-size:0.82rem; color:#64748B;">₹{total_inr:,.0f} &bull; {loc_sym}{total_loc:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col2:
        st.markdown(
            f"""
            <div class="metric-pill-box">
                <div class="metric-pill-lbl">Target Budget ({itinerary.budget_level})</div>
                <div class="metric-pill-val" style="color:#0F172A;">${target_budget:,.0f}</div>
                <div style="font-size:0.82rem; color:#64748B;">${target_budget/itinerary.duration_days:,.0f}/day benchmark</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col3:
        status_color = "#15803D" if budget_variance >= 0 else "#DC2626"
        status_text = f"+${budget_variance:,.0f} Under" if budget_variance >= 0 else f"-${abs(budget_variance):,.0f} Over"
        st.markdown(
            f"""
            <div class="metric-pill-box">
                <div class="metric-pill-lbl">Budget Variance</div>
                <div class="metric-pill-val" style="color:{status_color};">{status_text}</div>
                <div style="font-size:0.82rem; color:#64748B;">{"Within Target" if budget_variance >= 0 else "High-spend plan"}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col4:
        st.markdown(
            f"""
            <div class="metric-pill-box">
                <div class="metric-pill-lbl">Transit Efficiency</div>
                <div class="metric-pill-val" style="color:#0284C7;">100%</div>
                <div style="font-size:0.82rem; color:#64748B;">Geographic Clusters: {len(itinerary.days)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Budget Progress Bar
    pct = min(1.0, max(0.0, total_usd / target_budget if target_budget > 0 else 1.0))
    st.progress(pct, text=f"Budget Consumption: {pct*100:.1f}% of ${target_budget:,.0f} target")

    # =========================================================================
    # DAY-BY-DAY CLUSTERED ITINERARY VIEW
    # =========================================================================
    st.markdown("---")
    st.markdown("#### 📆 Structured Day-by-Day Schedule")

    for day in itinerary.days:
        with st.expander(f"📍 Day {day.day_number}: {day.theme} ({day.neighborhood_cluster})", expanded=(day.day_number <= 2)):
            # Cluster Header Banner
            st.markdown(
                f"""
                <div class="day-header-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <span class="day-title">Day {day.day_number}: {day.theme}</span>
                            <span class="day-cluster-pill">📍 {day.neighborhood_cluster}</span>
                        </div>
                        <div style="text-align:right;">
                            <span class="cost-badge" style="font-size:1rem;">
                                Day Total: ${day.daily_cost_usd:,.0f} &bull; ₹{day.daily_cost_inr:,.0f} ({loc_sym}{day.daily_cost_local:,.0f})
                            </span>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:#0F766E; margin-top:6px;">
                        🧭 <b>Transit Clustering:</b> {day.transit_summary}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Sequential Slots: Morning, Lunch, Afternoon, Evening
            for slot in day.slots:
                slot_type = slot.time_slot.lower()
                slot_class = "morning"
                if "lunch" in slot_type:
                    slot_class = "lunch"
                elif "afternoon" in slot_type:
                    slot_class = "afternoon"
                elif "evening" in slot_type:
                    slot_class = "evening"

                # Cost display formatted according to user selection
                if currency_view == "USD ($)":
                    cost_str = f"${slot.cost_usd:,.0f}"
                elif currency_view == "Indian Rupee (₹)":
                    cost_str = f"₹{slot.cost_inr:,.0f}"
                elif currency_view == "Local Only":
                    cost_str = f"{loc_sym}{slot.cost_local:,.0f}"
                else:
                    cost_str = f"{loc_sym}{slot.cost_local:,.0f} (${slot.cost_usd:,.0f} / ₹{slot.cost_inr:,.0f})"

                booking_badge = '<span class="tag-chip" style="background:#FEE2E2; color:#991B1B;">⚡ Reservation Advised</span>' if slot.booking_required else ''
                tags_html = "".join([f'<span class="tag-chip">{tag}</span>' for tag in slot.tags])

                st.markdown(
                    f"""
                    <div class="slot-card {slot_class}">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div class="slot-time">⏰ {slot.time_slot} ({slot.time_range}) &bull; <span style="color:#0284C7;">Cluster: {slot.neighborhood}</span></div>
                                <div class="slot-title">{slot.title}</div>
                            </div>
                            <div>
                                <span class="cost-badge">{cost_str}</span>
                            </div>
                        </div>
                        <div class="slot-desc">{slot.description}</div>
                        <div class="slot-transit">🚶‍♂️ {slot.transit_tip}</div>
                        <div class="slot-meta-row">
                            <div>
                                {tags_html}
                                {booking_badge}
                            </div>
                            <div style="font-size:0.75rem; color:#94A3B8;">Slot ID: {slot.slot_id}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Trip Highlights and Cultural Checklist
    st.markdown("---")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown("##### 🧳 Smart Packing Checklist")
        for item in itinerary.packing_checklist:
            st.markdown(f"- ✅ {item}")
    with c_col2:
        st.markdown("##### 💡 Local Etiquette & Transit Rules")
        for tip in itinerary.cultural_tips:
            st.markdown(f"- ℹ️ {tip}")
