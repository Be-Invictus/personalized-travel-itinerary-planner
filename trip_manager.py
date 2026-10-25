"""
Tab 4: Trip Management & Offline PDF Export.
Provides simulated database persistence (saving multiple trips, trip history viewer, load/delete)
and 1-click offline PDF travel guide generation with emergency checklists.
"""

import streamlit as st
from typing import Optional, List
from datetime import datetime

from models import Itinerary, TripRecord
from storage import get_all_trips, save_trip_record, delete_trip_record
from pdf_exporter import generate_itinerary_pdf


def render_trip_manager_tab(current_itinerary: Optional[Itinerary] = None):
    """Renders Tab 4 Trip Management & Offline PDF Export."""
    st.markdown("### 💾 Trip Management & Offline PDF Export")
    st.markdown(
        "Save and organize your travel itineraries with zero external database dependencies. "
        "Export an offline, print-ready PDF travel guide complete with local emergency numbers and packing checklists."
    )

    itinerary = current_itinerary or st.session_state.get("active_itinerary")

    # =========================================================================
    # SECTION 1: EXPORT CURRENT ITINERARY
    # =========================================================================
    st.markdown("---")
    st.markdown("#### 📄 Export Current Itinerary to Offline PDF")

    if itinerary:
        exp_col1, exp_col2 = st.columns([2, 1])
        with exp_col1:
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:16px;">
                    <div style="font-size:1.15rem; font-weight:700; color:#0F172A;">{itinerary.trip_title}</div>
                    <div style="font-size:0.85rem; color:#475569; margin:4px 0 10px 0;">
                        📍 {itinerary.destination}, {itinerary.country} &bull; {itinerary.duration_days} Days &bull; {itinerary.start_date} to {itinerary.end_date}
                    </div>
                    <div style="font-size:0.85rem; color:#15803D; font-weight:700;">
                        Total Budget: ${itinerary.total_cost_usd:,.0f} / ₹{itinerary.total_cost_inr:,.0f} ({itinerary.local_currency_symbol}{itinerary.total_cost_local:,.0f})
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with exp_col2:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            # Generate PDF in-memory
            try:
                pdf_bytes = generate_itinerary_pdf(itinerary)
                file_name = f"{itinerary.destination.split(',')[0].replace(' ', '_')}_Itinerary_Guide.pdf"
                st.download_button(
                    label="📥 Download Offline PDF Guide",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    help="Generates an offline-ready PDF with daily clusters, time slots, emergency contacts, and packing lists."
                )
                st.caption("✓ Includes 24/7 Emergency Contacts, Hospital details & route notes.")
            except Exception as e:
                st.error(f"Error compiling PDF: {str(e)}")

        # Save to Database Form
        st.markdown("---")
        st.markdown("#### 💾 Save Current Itinerary to Trip History")
        with st.form("save_trip_form"):
            s_col1, s_col2 = st.columns([1.5, 2])
            with s_col1:
                custom_trip_name = st.text_input("Trip Label / Title", value=itinerary.trip_title)
            with s_col2:
                user_notes = st.text_input("Personal Notes / Tags", placeholder="e.g. Anniversary getaway, Autumn foliage trip...")
            
            save_submitted = st.form_submit_button("💾 Save Trip to Simulated Database", type="secondary")
            if save_submitted:
                itinerary.trip_title = custom_trip_name
                record = save_trip_record(itinerary, user_notes=user_notes)
                st.success(f"Trip saved successfully! (Trip ID: {record.trip_id})")
                st.rerun()

    else:
        st.info("No active trip to export yet. Generate an itinerary in Tab 2 or load a saved trip below.")

    # =========================================================================
    # SECTION 2: TRIP HISTORY VIEWER (PERSISTENT DATABASE)
    # =========================================================================
    st.markdown("---")
    st.markdown("#### 📚 Saved Trips History & Archive")

    saved_trips: List[TripRecord] = get_all_trips()

    if not saved_trips:
        st.info("No saved trips in database yet. Generate a trip and click 'Save Trip' above!")
        return

    st.markdown(f"Found **{len(saved_trips)}** stored journeys in local persistent storage (`trips_db.json`).")

    for idx, trip in enumerate(saved_trips):
        with st.container():
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:10px; padding:14px 18px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <span style="font-size:1.15rem; font-weight:700; color:#0F172A;">{trip.trip_title}</span>
                        <span style="font-size:0.8rem; color:#64748B;">Saved: {trip.created_at}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#475569; margin:4px 0;">
                        📍 <b>{trip.destination}</b> &bull; {trip.duration_days} Days &bull; Est. Cost: <b>${trip.total_cost_usd:,.0f}</b>
                    </div>
                    <div style="font-size:0.82rem; color:#0284C7; font-style:italic;">
                        Notes: {trip.user_notes if trip.user_notes else 'No notes'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1.2, 1])
            with btn_col1:
                if st.button("📂 Load into Editor", key=f"load_{trip.trip_id}_{idx}"):
                    try:
                        restored_itinerary = Itinerary(**trip.itinerary_data)
                        st.session_state["active_itinerary"] = restored_itinerary
                        st.success(f"Loaded '{trip.trip_title}'! Switched to Tab 2.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to restore trip data: {str(e)}")

            with btn_col2:
                # PDF download direct from history
                try:
                    hist_itinerary = Itinerary(**trip.itinerary_data)
                    hist_pdf = generate_itinerary_pdf(hist_itinerary)
                    hist_name = f"{trip.destination.split(',')[0].replace(' ', '_')}_{trip.trip_id}.pdf"
                    st.download_button(
                        label="📄 Export PDF",
                        data=hist_pdf,
                        file_name=hist_name,
                        mime="application/pdf",
                        key=f"pdf_hist_{trip.trip_id}_{idx}"
                    )
                except Exception:
                    pass

            with btn_col3:
                if st.button("🗑️ Delete", key=f"del_{trip.trip_id}_{idx}", type="secondary"):
                    delete_trip_record(trip.trip_id)
                    st.warning(f"Deleted {trip.trip_title}")
                    st.rerun()

            st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
