import json
import time
import logging
import math
from pathlib import Path

from connectors import open_street_map
from data_classes import Location

# Locate project root (TRAVEL_FOOT) from this file’s location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = PROJECT_ROOT / "venues" / "venues.json"


logger = logging.getLogger(__name__)
_cache: dict[str, tuple[float, float]] = {}

if CACHE_FILE.exists():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    except json.JSONDecodeError:
        _cache = {}


def save_cache() -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as cf:
        json.dump(_cache, cf, indent=2, sort_keys=True, ensure_ascii=False)


def geocode_with_cache(query: str) -> Location | None:
    # TODO: consider unicoded query
    if query in _cache:
        lat, lon = _cache[query]
        return Location(lat, lon)

    # Throttle: respect Nominatim's 1 request/sec
    time.sleep(1)
    data = open_street_map.venue_location(query)

    if not data:
        logger.error("No geocoding data found for query: %s", query)
        return None

    lat, lon = (float(data[0]["lat"]), float(data[0]["lon"]))
    _cache[query] = (lat, lon)
    save_cache()
    return Location(lat, lon)


def haversine_distance(loc1: Location, loc2: Location) -> float:
    """
    Compute the distance between two Locations in kilometers.
    """
    lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
    lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    radius_earth_km = 6371.0
    return radius_earth_km * c
