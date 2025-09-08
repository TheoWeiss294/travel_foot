import json
import time
import math
from pathlib import Path
from typing import NamedTuple

from connectors import open_street_map

# Locate project root (TRAVEL_FOOT) from this file’s location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = PROJECT_ROOT / "venues" / "venues.json"


class Location(NamedTuple):
    latitude: float
    longitude: float


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
        json.dump(_cache, cf, indent=2, sort_keys=True)


def geocode_with_cache(query: str) -> Location | None:
    if query in _cache:
        lat, lon = _cache[query]
        return Location(lat, lon)

    # Throttle: respect Nominatim's 1 request/sec
    time.sleep(1)
    data = open_street_map.venue_location(query)

    if not data:
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
