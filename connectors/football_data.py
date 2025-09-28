import os
from typing import Any, NamedTuple
from enum import StrEnum
from datetime import datetime

import requests


API_KEY = os.environ.get("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"


class LeagueId(StrEnum):
    CHAMPIONS_LEAGUE = "CL"
    PREMIER_LEAGUE = "PL"


class FixturesParams(NamedTuple):
    league_id: LeagueId
    start_date: datetime
    end_date: datetime


def get_football_data(
    url: str, headers: dict[str, Any], params: dict[str, Any]
) -> dict[str, Any]:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_upcoming_fixtures(params: FixturesParams) -> dict[str, Any]:
    return get_football_data(
        url=f"{BASE_URL}/competitions/{params.league_id}/matches",
        headers={"X-Auth-Token": API_KEY},
        params={
            "dateFrom": params.start_date.strftime("%Y-%m-%d"),
            "dateTo": params.end_date.strftime("%Y-%m-%d"),
        },
    )


def get_competition_teams(league_id: LeagueId) -> dict[str, Any]:
    return get_football_data(
        url=f"{BASE_URL}/competitions/{league_id}/teams",
        headers={"X-Auth-Token": API_KEY},
        params={},  # optional, current season by default
    )


def get_champions_league_fixtures(
    start_date: datetime, end_date: datetime
) -> dict[str, Any]:
    return get_upcoming_fixtures(
        FixturesParams(LeagueId.CHAMPIONS_LEAGUE, start_date, end_date)
    )
