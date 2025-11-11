from typing import NamedTuple, TypeAlias
from datetime import datetime


WeightedAdjacencyDict: TypeAlias = dict[int, int]


class NodeAdjacency(NamedTuple):
    incoming: WeightedAdjacencyDict
    outgoing: WeightedAdjacencyDict


MatchGraph: TypeAlias = list[NodeAdjacency]


class Location(NamedTuple):
    latitude: float
    longitude: float


class Match(NamedTuple):
    home_team: str
    away_team: str
    date: datetime
    location: Location

    def __repr__(self) -> str:
        return f"{self.home_team} vs {self.away_team}"


class Matchday(NamedTuple):
    date: datetime
    matches: set[Match]

    def __repr__(self) -> str:
        return f"{self.date}: " + " | ".join(self.matches)


MatchPath: TypeAlias = list[Matchday]
