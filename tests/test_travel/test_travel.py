from datetime import datetime, timedelta

from travel import travel
from data_classes import Location, Match


CRAVEN_COTTAGE = Location(51.4749218, -0.2217448)
STAMFORD_BRIDGE = Location(51.4816869, -0.1910336)
TOTTENHAM_STADIUM = Location(51.604157, -0.0662604)

DEFAULT_LOCATION = STAMFORD_BRIDGE
DEFAULT_DATE = datetime(2025, 9, 1)

MATCHES_EXAMPLE = [
    Match("G", "H", datetime(2025, 9, 5), Location(48.2188, 11.6236)),
    Match("C", "D", datetime(2025, 9, 3), Location(51.4925, 7.4517)),
    Match("A", "B", datetime(2025, 9, 1), Location(48.2188, 11.6236)),
    Match("E", "F", datetime(2025, 9, 4), Location(1.4925, 37.4517)),
]


def test_travel_graph__init() -> None:
    matches = MATCHES_EXAMPLE
    travel_graph = travel.TravelGraph(matches, max_dist=500, max_days=3)

    sorted_matches = [matches[2], matches[1], matches[3], matches[0]]
    assert travel_graph.matches == sorted_matches
    assert travel_graph.total_days == 3
    assert travel_graph.graph == [{1: 2}, {3: 2}, {}, {}]


def test_find_paths__sanity() -> None:
    matches = MATCHES_EXAMPLE
    travel_graph = travel.TravelGraph(matches, max_dist=500, max_days=3)

    paths = travel_graph.find_paths(min_games=3)
    assert not paths

    paths = travel_graph.find_paths(min_games=2)
    assert paths == [
        [matches[2], matches[1]],
        [matches[1], matches[0]],
    ]

    travel_graph = travel.TravelGraph(matches, max_dist=500, max_days=5)
    paths = travel_graph.find_paths(min_games=3)
    assert paths == [[matches[2], matches[1], matches[0]]]


def test_find_paths__remove_subsequences() -> None:
    matches = [
        _match(index=1, days=0, loc=TOTTENHAM_STADIUM),
        _match(index=2, days=2, loc=CRAVEN_COTTAGE),
        _match(index=3, days=3, loc=STAMFORD_BRIDGE),
        _match(index=4, days=4, loc=STAMFORD_BRIDGE),
        _match(index=5, days=5, loc=STAMFORD_BRIDGE),
    ]
    expected_output = [matches[1:]]

    travel_graph = travel.TravelGraph(matches, max_dist=10, max_days=5)
    paths = travel_graph.find_paths(min_games=3)
    assert paths == expected_output


def _match(index: int, days: int, loc: Location = DEFAULT_LOCATION) -> Match:
    return Match(
        home_team=f"A{index}",
        away_team=f"B{index}",
        date=DEFAULT_DATE + timedelta(days=days),
        location=loc,
    )
