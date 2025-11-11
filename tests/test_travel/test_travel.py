from datetime import datetime, timedelta
from itertools import combinations

from travel import travel
from data_classes import Location, Match, MatchGraph, NodeAdjacency


CRAVEN_COTTAGE = Location(51.4749218, -0.2217448)
EMIRATES_STADIUM = Location(51.5550403, -0.1083997)
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
    expected = MatchGraph(
        [
            NodeAdjacency({}, {1: 2}),
            NodeAdjacency({0: 2}, {3: 2}),
            NodeAdjacency({}, {}),
            NodeAdjacency({1: 2}, {}),
        ]
    )

    sorted_matches = [matches[2], matches[1], matches[3], matches[0]]
    assert travel_graph.matches == sorted_matches
    assert travel_graph.total_days == 3
    assert travel_graph.graph == expected


def test_travel_graph__equivalent_nodes() -> None:
    matches = [
        _match(index=1, days=0, loc=EMIRATES_STADIUM),
        _match(index=2, days=2, loc=CRAVEN_COTTAGE),
        _match(index=3, days=2, loc=STAMFORD_BRIDGE, hours=1),
        _match(index=4, days=3, loc=TOTTENHAM_STADIUM),
        _match(index=5, days=4, loc=EMIRATES_STADIUM),
    ]
    expected_graph = MatchGraph(
        [
            NodeAdjacency({}, {1: 2, 2: 2, 3: 3}),
            NodeAdjacency({0: 2}, {4: 2}),
            NodeAdjacency({0: 2}, {4: 2}),
            NodeAdjacency({0: 3}, {4: 1}),
            NodeAdjacency({1: 2, 2: 2, 3: 1}, {}),
        ]
    )

    travel_graph = travel.TravelGraph(matches, max_dist=12, max_days=4)
    assert travel_graph.graph == expected_graph

    # pylint: disable=protected-access
    equivalent_tuples = [
        (i, j)
        for i, j in combinations(range(len(matches)), 2)
        if travel_graph._equivalence_key(i) == travel_graph._equivalence_key(j)
    ]
    assert equivalent_tuples == [(1, 2)]


def test_travel_graph__equivalent_node__sanity() -> None:
    matches = [
        _match(index=0, days=0, loc=EMIRATES_STADIUM),
        _match(index=1, days=2, loc=CRAVEN_COTTAGE),
        _match(index=2, days=2, loc=STAMFORD_BRIDGE, hours=1),
        _match(index=3, days=3, loc=TOTTENHAM_STADIUM),
        _match(index=4, days=4, loc=EMIRATES_STADIUM),
        _match(index=5, days=7, loc=CRAVEN_COTTAGE),
        _match(index=6, days=7, loc=STAMFORD_BRIDGE, hours=1),
        _match(index=7, days=7, loc=TOTTENHAM_STADIUM, hours=2),
        _match(index=8, days=17, loc=TOTTENHAM_STADIUM),
        _match(index=9, days=17, loc=EMIRATES_STADIUM, hours=2),
    ]
    travel_graph = travel.TravelGraph(matches, max_dist=12, max_days=4)
    equiv_groups = list(travel_graph.equiv_dict.values())
    assert equiv_groups == [[0], [1, 2], [3], [4], [5, 6, 7], [8], [9]]


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


def test_find_paths__basic():
    matches = [
        _match(index=0, days=0),
        _match(index=1, days=2),
        _match(index=2, days=4),
        _match(index=3, days=10),
    ]
    expected_output = [matches[:3]]
    travel_graph = travel.TravelGraph(matches, max_dist=10, max_days=5)
    paths = travel_graph.find_paths(2)

    assert paths == expected_output


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


def test_find_paths__testcase_1() -> None:
    matches = [
        _match(index=0, days=0, loc=TOTTENHAM_STADIUM),
        _match(index=1, days=0, hours=1, loc=STAMFORD_BRIDGE),
        _match(index=2, days=1, loc=STAMFORD_BRIDGE),
        _match(index=3, days=2, loc=STAMFORD_BRIDGE),
        _match(index=4, days=2, hours=1, loc=TOTTENHAM_STADIUM),
        _match(index=5, days=3, loc=TOTTENHAM_STADIUM),
    ]
    expected = [
        [matches[0], matches[2], matches[3], matches[5]],
        [matches[0], matches[2], matches[4], matches[5]],
        [matches[1], matches[2], matches[3], matches[5]],
        [matches[1], matches[2], matches[4], matches[5]],
    ]
    travel_graph = travel.TravelGraph(matches, max_dist=50, max_days=5)
    paths = travel_graph.find_paths(min_games=3)
    assert paths == expected


def test__sparse_graph__sanity() -> None:
    matches = [
        _match(index=0, days=0, loc=EMIRATES_STADIUM),
        _match(index=1, days=2, loc=CRAVEN_COTTAGE),
        _match(index=2, days=2, loc=STAMFORD_BRIDGE, hours=1),
        _match(index=3, days=3, loc=TOTTENHAM_STADIUM),
        _match(index=4, days=4, loc=EMIRATES_STADIUM),
    ]
    travel_graph = travel.TravelGraph(matches, max_dist=12, max_days=4)
    sparse_graph = travel_graph._sparse_graph()  # pylint: disable=protected-access
    assert sparse_graph == {0: {1: 2, 3: 3}, 1: {4: 2}, 3: {4: 1}, 4: {}}


def _match(
    index: int, days: int, hours: int = 0, loc: Location = DEFAULT_LOCATION
) -> Match:
    return Match(
        home_team=f"A{index}",
        away_team=f"B{index}",
        date=DEFAULT_DATE + timedelta(days=days, hours=hours),
        location=loc,
    )
