from datetime import datetime

from travel import travel
from data_classes import Location, Match


CRAVEN_COTTAGE = Location(51.4749218, -0.2217448)
STAMFORD_BRIDGE = Location(51.4816869, -0.1910336)
TOTTENHAM_STADIUM = Location(51.604157, -0.0662604)


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


def test_find_path_with_candidate__sanity() -> None:
    travel_graph = travel.TravelGraph(MATCHES_EXAMPLE, max_dist=500, max_days=3)

    output = []
    travel_graph.find_path_with_candidate(
        candidate=[1], min_games=2, days_left=3, output=output
    )
    assert output == [[MATCHES_EXAMPLE[1], MATCHES_EXAMPLE[0]]]


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
        Match("A1", "A2", datetime(2022, 1, 1), TOTTENHAM_STADIUM),
        Match("B1", "B2", datetime(2022, 1, 3), CRAVEN_COTTAGE),
        Match("C1", "C2", datetime(2022, 1, 4), STAMFORD_BRIDGE),
        Match("D1", "D2", datetime(2022, 1, 5), STAMFORD_BRIDGE),
        Match("E1", "E2", datetime(2022, 1, 6), STAMFORD_BRIDGE),
    ]
    expected_output = [matches[1:]]

    travel_graph = travel.TravelGraph(matches, max_dist=10, max_days=5)
    paths = travel_graph.find_paths(min_games=3)
    assert paths == expected_output
