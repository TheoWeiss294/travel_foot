from typing import NamedTuple
from datetime import datetime


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


class Gameday(NamedTuple):
    date: datetime
    matches: set[int]
