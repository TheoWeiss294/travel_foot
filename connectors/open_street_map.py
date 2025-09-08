from typing import Any
import requests

URL = "https://nominatim.openstreetmap.org/search"


def venue_location(query: str) -> list[dict[str, Any]]:
    params = {"q": query, "format": "json", "limit": 1}
    response = requests.get(
        URL, params=params, headers={"User-Agent": "travel-foot"}, timeout=10
    )
    response.raise_for_status()
    return response.json()
