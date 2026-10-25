"""
Tab 3: Vibe Customization & Dynamic Activity Swap.
Provides interactive controls to modify specific slots or single days without wiping the master plan.
"""

import streamlit as st
from typing import Optional
from models import Itinerary, ActivitySlot, DayPlan
from llm_service import LLMService


def render_customizer_tab(llm_service: LLMService):
    """Renders the Tab 3 Activity Customization & Dynamic Swap UI."""
    st.markdown("### ⚡ Vibe Customization & Dynamic Activity Swap")
    st.markdown(
        "Tailor your itinerary on the fly. Swap individual morning sightseeing, lunch spots, or evening venues "
        "to match sudden mood shifts or dietary preferences—**without altering or resetting the rest of your trip**."
    )

    itinerary: Optional[Itinerary] = st.session_state.get("active_itinerary")

    if not itinerary or not itinerary.days:
        st.warning("⚠️ No active itinerary found! Please generate an itinerary in Tab 2 or load a saved trip in Tab 4 first.")
        return

    st.markdown(f"**Editing Active Trip:** *{itinerary.trip_title}* ({itinerary.destination})")

    # Day Selector
    day_numbers = [d.day_number for d in itinerary.days]
    selected_day_num = st.selectbox(
        "Select Day to Customize",
        options=day_numbers,
        format_func=lambda d: f"Day {d}: {next((day.theme for day in itinerary.days if day.day_number == d), '')} ({next((day.neighborhood_cluster for day in itinerary.days if day.day_number == d), '')})"
    )

    target_day = next(d for d in itinerary.days if d.day_number == selected_day_num)

    col_slot, col_intent = st.columns([1.2, 1.8])

    with col_slot:
        slot_labels = [f"{s.time_slot} ({s.time_range}) - {s.title[:30]}..." for s in target_day.slots]
        selected_slot_idx = st.selectbox(
            "Select Time Slot to Modify",
            options=range(len(target_day.slots)),
            format_func=lambda idx: slot_labels[idx]
        )
        current_slot: ActivitySlot = target_day.slots[selected_slot_idx]

    with col_intent:
        preset_intent = st.selectbox(
            "Quick Swap Presets",
            options=[
                "Find authentic vegetarian / vegan lunch spot",
                "Swap for bustling outdoor artisan street market",
                "More relaxed scenic garden & cafe vibe",
                "High-adrenaline adventure or active trek",
                "Historic architecture & hidden courtyard tour",
                "Custom user request (write below)"
            ]
        )

        custom_intent_text = st.text_input(
            "Custom Swap Prompt / Specific Request",
            value="" if preset_intent != "Custom user request (write below)" else "Swap for cozy acoustic jazz lounge",
            placeholder="e.g. Vegetarian street tacos, rooftop photography spot, quiet museum..."
        )

    swap_prompt = custom_intent_text.strip() if custom_intent_text.strip() else preset_intent

    # Current Slot Preview Box
    st.markdown("##### Current Slot Details (Before Swap)")
    st.markdown(
        f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:4px solid #64748B; border-radius:8px; padding:12px 16px; margin-bottom:14px;">
            <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">
                {current_slot.time_slot} ({current_slot.time_range}) &bull; Cluster: {current_slot.neighborhood}
            </div>
            <div style="font-size:1.05rem; font-weight:700; color:#0F172A; margin:3px 0;">{current_slot.title}</div>
            <div style="font-size:0.9rem; color:#475569;">{current_slot.description}</div>
            <div style="font-size:0.82rem; color:#15803D; font-weight:600; margin-top:4px;">
                Est. Cost: ${current_slot.cost_usd:,.0f} / ₹{current_slot.cost_inr:,.0f} ({itinerary.local_currency_symbol}{current_slot.cost_local:,.0f})
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    action_col1, action_col2 = st.columns([1.5, 1])

    with action_col1:
        if st.button("⚡ Swap This Slot Now", type="primary", use_container_width=True):
            with st.spinner(f"Curating replacement activity within {target_day.neighborhood_cluster}..."):
                try:
                    new_slot = llm_service.swap_activity_slot(
                        current_slot=current_slot,
                        day_theme=target_day.theme,
                        neighborhood_cluster=target_day.neighborhood_cluster,
                        destination=itinerary.destination,
                        swap_intent=swap_prompt,
                        budget_level=itinerary.budget_level,
                        currency_code=itinerary.local_currency_code,
                        usd_rate=itinerary.usd_exchange_rate,
                        inr_rate=itinerary.inr_exchange_rate
                    )

                    # Update slot in day
                    target_day.slots[selected_slot_idx] = new_slot

                    # Recalculate day totals
                    new_day_local = sum(s.cost_local for s in target_day.slots)
                    new_day_usd = sum(s.cost_usd for s in target_day.slots)
                    new_day_inr = sum(s.cost_inr for s in target_day.slots)
                    target_day.daily_cost_local = round(new_day_local, 2)
                    target_day.daily_cost_usd = round(new_day_usd, 2)
                    target_day.daily_cost_inr = round(new_day_inr, 2)

                    # Recalculate itinerary grand totals
                    itinerary.total_cost_local = round(sum(d.daily_cost_local for d in itinerary.days), 2)
                    itinerary.total_cost_usd = round(sum(d.daily_cost_usd for d in itinerary.days), 2)
                    itinerary.total_cost_inr = round(sum(d.daily_cost_inr for d in itinerary.days), 2)

                    # Store in session state
                    st.session_state["active_itinerary"] = itinerary
                    st.session_state["last_swapped_slot"] = {
                        "day": selected_day_num,
                        "slot": new_slot,
                        "old_title": current_slot.title
                    }
                    st.success(f"Successfully swapped {current_slot.time_slot} activity!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to swap activity: {str(e)}")

    with action_col2:
        if st.button(f"🔄 Re-balance Day {selected_day_num} Budget", use_container_width=True):
            st.info(f"Day {selected_day_num} costs re-indexed against current exchange rates.")

    # Show Last Swapped Diff Notice
    if "last_swapped_slot" in st.session_state:
        swap_info = st.session_state["last_swapped_slot"]
        swapped_slot: ActivitySlot = swap_info["slot"]
        st.markdown("---")
        st.markdown("#### ✨ Newly Swapped Activity Slot")
        st.markdown(
            f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-left:4px solid #22C55E; border-radius:8px; padding:14px 18px;">
                <div style="font-size:0.8rem; font-weight:700; color:#15803D; text-transform:uppercase;">
                    ✓ Updated Day {swap_info['day']} &bull; {swapped_slot.time_slot} ({swapped_slot.time_range})
                </div>
                <div style="font-size:1.15rem; font-weight:700; color:#0F172A; margin:4px 0;">{swapped_slot.title}</div>
                <div style="font-size:0.92rem; color:#334155; margin-bottom:6px;">{swapped_slot.description}</div>
                <div style="font-size:0.82rem; color:#0284C7;">🚶‍♂️ <b>Cluster Route:</b> {swapped_slot.transit_tip}</div>
                <div style="font-size:0.85rem; color:#15803D; font-weight:700; margin-top:8px;">
                    Updated Cost: ${swapped_slot.cost_usd:,.0f} / ₹{swapped_slot.cost_inr:,.0f} ({itinerary.local_currency_symbol}{swapped_slot.cost_local:,.0f})
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
