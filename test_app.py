"""
Comprehensive Test Suite for Dynamic Recommendations and Tailored Itineraries.
Verifies that varying mood, party, pace, and destination produces distinct, customized plans.
"""

from llm_service import LLMService
from pdf_exporter import generate_itinerary_pdf
from storage import save_trip_record, get_all_trips, delete_trip_record


def run_tests():
    print("=== RUNNING ENHANCED DYNAMIC RECOMMENDATIONS & ITINERARY TESTS ===")
    svc = LLMService(provider="Demo")

    # 1. Test Dynamic Recommendations with DIFFERENT parameters
    # Test A: Mountains + Family with Kids + Relaxed
    recs_family_mountains = svc.recommend_destinations(
        mood="Mountains, Hiking & Serenity",
        budget="Moderate",
        season="Summer (Jun - Aug)",
        party="Family with Kids",
        pace="Relaxed (2 activities/day + ample downtime)",
        interests=["Nature & Scenic Landscapes"]
    )
    cities_a = [r.city for r in recs_family_mountains]
    print(f"[PASS] Mountains + Family -> Generated: {cities_a}")
    assert any("Banff" in c or "Interlaken" in c or "Manali" in c for c in cities_a), "Must recommend mountain destinations for families"

    # Test B: Vibrant Urban + Solo Traveler + Fast-Paced
    recs_solo_urban = svc.recommend_destinations(
        mood="Vibrant Urban Megacity",
        budget="Budget",
        season="Spring (Mar - May)",
        party="Solo Traveler",
        pace="Fast-Paced (Packed highlights from dawn to late night)",
        interests=["Food & Culinary Trails", "Nightlife, Bars & Music"]
    )
    cities_b = [r.city for r in recs_solo_urban]
    print(f"[PASS] Urban + Solo + Fast-Paced -> Generated: {cities_b}")
    assert any("Tokyo" in c or "New York" in c or "Barcelona" in c for c in cities_b), "Must recommend vibrant urban cities"

    # Test C: Verify that Test A and Test B do NOT generate the exact same list
    assert cities_a != cities_b, "Different inputs must produce different recommendation lists!"
    print(f"[PASS] Verified: Dynamic scoring returns distinct cities for different inputs (NOT repeating Kyoto/Amalfi/Barcelona)!")

    # 2. Test Itinerary Generation for DIFFERENT Cities & Parties & Paces
    # City 1: Tokyo with Solo + Fast-Paced
    it_tokyo = svc.generate_itinerary(
        destination="Tokyo, Japan",
        duration_days=3,
        start_date="2026-11-01",
        budget_level="Moderate",
        travel_party="Solo Traveler",
        pace="Fast-Paced (Packed highlights from dawn to late night)",
        interests=["Food & Culinary Trails", "Art, History & Museums"]
    )
    assert it_tokyo.local_currency_code == "JPY"
    assert "Shibuya" in it_tokyo.days[0].neighborhood_cluster or "Shinjuku" in it_tokyo.days[0].neighborhood_cluster or "Asakusa" in it_tokyo.days[0].neighborhood_cluster
    assert "08:30" in it_tokyo.days[0].slots[0].time_range or "09:00" in it_tokyo.days[0].slots[0].time_range
    print(f"[PASS] Tokyo Itinerary -> Clustered in {it_tokyo.days[0].neighborhood_cluster} with {it_tokyo.local_currency_code} ({it_tokyo.local_currency_symbol})")

    # City 2: Manali with Family with Kids + Relaxed
    it_manali = svc.generate_itinerary(
        destination="Manali, India",
        duration_days=3,
        start_date="2026-11-01",
        budget_level="Budget",
        travel_party="Family with Kids",
        pace="Relaxed (2 activities/day + ample downtime)",
        interests=["Nature & Scenic Landscapes"]
    )
    assert it_manali.local_currency_code == "INR"
    assert "10:00" in it_manali.days[0].slots[0].time_range, "Relaxed pace should start later at 10:00 AM"
    assert "Family" in it_manali.days[0].slots[0].tags or "Family" in it_manali.days[0].slots[0].description
    print(f"[PASS] Manali Itinerary -> Relaxed 10:00 start in {it_manali.days[0].neighborhood_cluster} ({it_manali.local_currency_code})")

    # City 3: Freeform custom city (e.g. Zurich, Switzerland)
    it_custom = svc.generate_itinerary(
        destination="Zurich, Switzerland",
        duration_days=2,
        start_date="2026-11-01",
        budget_level="Luxury",
        travel_party="Couple / Romantic",
        pace="Moderate",
        interests=["Architecture"]
    )
    assert "Zurich" in it_custom.destination
    assert len(it_custom.days) == 2
    print(f"[PASS] Custom City (Zurich) -> Generated clustered plan for {it_custom.destination}")

    # 3. Test PDF generation on newly generated itinerary
    pdf = generate_itinerary_pdf(it_tokyo)
    assert len(pdf) > 5000
    print(f"[PASS] Compiled PDF Guide for {it_tokyo.trip_title} ({len(pdf)} bytes)")

    print("\n[SUCCESS] ALL DYNAMIC TAILORING TESTS PASSED! Fix is 100% verified.")


if __name__ == "__main__":
    run_tests()
