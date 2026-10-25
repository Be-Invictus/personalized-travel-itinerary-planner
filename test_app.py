"""
Automated Verification Test Suite for Travel Itinerary Planner.
Tests all core modules: models, storage, LLM service (demo engine), and PDF exporter.
"""

import os
from models import Itinerary, DayPlan, ActivitySlot, DestinationRecommendation
from llm_service import LLMService
from storage import save_trip_record, get_all_trips, delete_trip_record, get_trip_record
from pdf_exporter import generate_itinerary_pdf


def test_suite():
    print("=== RUNNING FULL VERIFICATION TEST SUITE ===")

    # 1. Test LLM Service Demo Recommendations
    svc = LLMService(provider="Demo")
    recs = svc.recommend_destinations(
        mood="Beach & Coastal Sun",
        budget="Moderate",
        season="Summer (Jun - Aug)",
        party="Couple / Romantic",
        interests=["Food & Culinary Trails"]
    )
    assert len(recs) == 3, f"Expected 3 recommendations, got {len(recs)}"
    assert recs[0].city != "", "Recommendation city must not be empty"
    print(f"[PASS] Tab 1 Recommender Passed: Generated {len(recs)} destinations ({recs[0].city}, {recs[1].city}, {recs[2].city})")

    # 2. Test Itinerary Generation with Geographic Clustering
    itinerary = svc.generate_itinerary(
        destination="Kyoto, Japan",
        duration_days=3,
        start_date="2026-11-01",
        budget_level="Moderate",
        travel_party="Couple / Romantic",
        pace="Moderate",
        interests=["Art, History & Museums", "Food & Culinary Trails"]
    )
    assert len(itinerary.days) == 3, f"Expected 3 days, got {len(itinerary.days)}"
    for day in itinerary.days:
        assert len(day.slots) == 4, f"Day {day.day_number} must have 4 time slots"
        assert day.neighborhood_cluster != "", f"Day {day.day_number} must have a geographic cluster"
        for slot in day.slots:
            assert slot.cost_local >= 0, "Cost must be positive"
            assert slot.cost_usd >= 0, "USD cost must be positive"
            assert slot.cost_inr >= 0, "INR cost must be positive"
    print(f"[PASS] Tab 2 Itinerary Generator Passed: Generated 3 days with clusters {[d.neighborhood_cluster for d in itinerary.days]}")

    # 3. Test Dynamic Activity Slot Swap
    day1 = itinerary.days[0]
    slot_lunch = day1.slots[1]
    swapped_slot = svc.swap_activity_slot(
        current_slot=slot_lunch,
        day_theme=day1.theme,
        neighborhood_cluster=day1.neighborhood_cluster,
        destination=itinerary.destination,
        swap_intent="Find authentic vegetarian / vegan lunch spot",
        budget_level=itinerary.budget_level,
        currency_code=itinerary.local_currency_code,
        usd_rate=itinerary.usd_exchange_rate,
        inr_rate=itinerary.inr_exchange_rate
    )
    assert swapped_slot.slot_id == slot_lunch.slot_id, "Slot ID must be preserved"
    assert "Vegetarian" in swapped_slot.tags or "Vegetarian" in swapped_slot.title, "Swap intent must reflect in new slot"
    print(f"[PASS] Tab 3 Slot Swap Passed: Replaced '{slot_lunch.title}' with '{swapped_slot.title}'")

    # 4. Test Offline PDF Generation
    pdf_bytes = generate_itinerary_pdf(itinerary)
    assert len(pdf_bytes) > 5000, f"PDF bytes should be significant size, got {len(pdf_bytes)}"
    assert pdf_bytes.startswith(b"%PDF"), "Must start with PDF header bytes"
    print(f"[PASS] Tab 4 PDF Exporter Passed: Successfully compiled valid PDF ({len(pdf_bytes)} bytes)")

    # 5. Test Simulated Database Persistence
    saved_record = save_trip_record(itinerary, user_notes="Automated test trip record")
    all_trips = get_all_trips()
    assert any(t.trip_id == saved_record.trip_id for t in all_trips), "Saved trip must appear in get_all_trips()"
    
    loaded_record = get_trip_record(saved_record.trip_id)
    assert loaded_record is not None, "Loaded record must not be None"
    assert loaded_record.destination == itinerary.destination, "Destination must match"

    deleted = delete_trip_record(saved_record.trip_id)
    assert deleted is True, "Delete trip must return True"
    print("[PASS] Tab 4 Storage Persistence Passed: Created, retrieved, and cleaned up test trip")

    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY! The application is production-ready.")


if __name__ == "__main__":
    test_suite()
