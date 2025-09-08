# pylint: disable=protected-access

import json
from unittest.mock import patch, MagicMock
from venues import venues
from venues.venues import Location


def test_geocode_with_cache__in_cache(monkeypatch):
    venues._cache.clear()
    venues._cache["Allianz Arena"] = (48.2188, 11.6236)

    mock_api = MagicMock()
    monkeypatch.setattr(venues.open_street_map, "venue_location", mock_api)

    coords = venues.geocode_with_cache("Allianz Arena")

    assert coords == Location(48.2188, 11.6236)


def test_geocode_with_cache__not_in_cache():
    venues._cache.clear()
    fake_response = [{"lat": "40.1235", "lon": "20.6543"}]

    with patch.object(venues, "save_cache", lambda: None), patch.object(
        venues.open_street_map, "venue_location", return_value=fake_response
    ):
        coords = venues.geocode_with_cache("Some Stadium")

    assert coords == Location(40.1235, 20.6543)
    assert venues._cache["Some Stadium"] == (40.1235, 20.6543)


def test_save_cache_does_not_touch_file(tmp_path, monkeypatch):
    monkeypatch.setattr(venues, "CACHE_FILE", tmp_path / "venues.json")
    venues._cache.clear()
    venues._cache["Test Stadium"] = (1.2345, 6.7890)

    venues.save_cache()
    loaded = json.loads((tmp_path / "venues.json").read_text())
    assert loaded["Test Stadium"] == [1.2345, 6.7890]


def test_haversine_distance__sanity() -> None:
    allianz = Location(48.2188, 11.6236)
    signal_iduna = Location(51.4925, 7.4517)
    distance_km = venues.haversine_distance(allianz, signal_iduna)
    assert round(distance_km, 3) == 470.965
