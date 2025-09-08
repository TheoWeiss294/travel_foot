from connectors import open_street_map


def test_venue_location__sanity() -> None:
    venue_name = "Allianz Arena"
    data = open_street_map.venue_location(venue_name)

    assert data
    coords = (float(data[0]["lat"]), float(data[0]["lon"]))
    assert coords == (48.2187901, 11.6236227)
