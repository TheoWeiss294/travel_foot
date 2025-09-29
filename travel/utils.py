from datetime import datetime
from venues import haversine_distance

from data_classes import Match, MatchGraph


def calc_incoming_degrees(graph: MatchGraph) -> list[int]:
    incoming_degrees = [0 for _ in range(len(graph))]
    for neighbors_dict in graph:
        for neighbour in neighbors_dict.keys():
            incoming_degrees[neighbour] += 1
    return incoming_degrees


def days_between(m1: Match, m2: Match) -> int:
    return days_between_dates(m1.date, m2.date)


def days_between_dates(d1: datetime, d2: datetime) -> int:
    return (d2.date() - d1.date()).days


def dist_between(m1: Match, m2: Match) -> float:
    return haversine_distance(m1.location, m2.location)
