"""
Simulated Database Persistence Layer (Zero external DB dependencies).
Stores trips in a local JSON database (trips_db.json) and synchronizes with Streamlit session state.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from models import TripRecord, Itinerary

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "trips_db.json")


def _read_db() -> Dict[str, Any]:
    """Reads the JSON database from disk."""
    if not os.path.exists(DB_FILE_PATH):
        return {"trips": {}}
    try:
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "trips" not in data:
                return {"trips": {}}
            return data
    except Exception:
        return {"trips": {}}


def _write_db(data: Dict[str, Any]) -> bool:
    """Writes the dictionary to the JSON database on disk."""
    try:
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_all_trips() -> List[TripRecord]:
    """Retrieves all saved trips sorted by creation date descending."""
    db = _read_db()
    records = []
    for trip_id, t_dict in db.get("trips", {}).items():
        try:
            records.append(TripRecord(**t_dict))
        except Exception:
            continue
    records.sort(key=lambda r: r.created_at, reverse=True)
    return records


def save_trip_record(itinerary: Itinerary, user_notes: str = "") -> TripRecord:
    """Saves or updates an itinerary in the database."""
    db = _read_db()
    trip_id = f"trip_{uuid.uuid4().hex[:8]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = TripRecord(
        trip_id=trip_id,
        created_at=now_str,
        updated_at=now_str,
        trip_title=itinerary.trip_title,
        destination=itinerary.destination,
        duration_days=itinerary.duration_days,
        total_cost_usd=itinerary.total_cost_usd,
        itinerary_data=itinerary.model_dump(),
        user_notes=user_notes
    )

    db["trips"][trip_id] = record.model_dump()
    _write_db(db)
    return record


def delete_trip_record(trip_id: str) -> bool:
    """Deletes a trip by trip_id."""
    db = _read_db()
    if trip_id in db.get("trips", {}):
        del db["trips"][trip_id]
        return _write_db(db)
    return False


def get_trip_record(trip_id: str) -> Optional[TripRecord]:
    """Retrieves a single trip record by ID."""
    db = _read_db()
    data = db.get("trips", {}).get(trip_id)
    if data:
        return TripRecord(**data)
    return None


def seed_sample_trip_if_empty(sample_itinerary: Itinerary):
    """Seeds one sample trip if database is currently empty."""
    db = _read_db()
    if not db.get("trips"):
        save_trip_record(sample_itinerary, user_notes="Pre-loaded sample trip for exploration.")
