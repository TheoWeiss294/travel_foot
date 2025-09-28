from datetime import datetime, timezone

from connectors import football_data
from data_classes import Match
from venues import geocode_with_cache

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_all_matches(start_date: datetime, end_date: datetime) -> None:
    matches = []
    for league_id in football_data.LeagueId:
        matches.extend(get_league_matches(league_id, start_date, end_date))
    return matches


def get_league_matches(
    league_id: football_data.LeagueId, start_date: datetime, end_date: datetime
) -> None:
    params = football_data.FixturesParams(league_id, start_date, end_date)
    fixtures = football_data.get_upcoming_fixtures(params)
    data = football_data.get_competition_teams(league_id)
    home_grounds = {
        team["name"]: team["venue"] for team in data["teams"] if team["venue"]
    }

    return [
        Match(
            f["homeTeam"]["name"],
            f["awayTeam"]["name"],
            datetime.strptime(f["utcDate"], TIME_FORMAT).replace(tzinfo=timezone.utc),
            location,
        )
        for f in fixtures["matches"]
        if (venue := f.get("venue", home_grounds.get(f["homeTeam"]["name"])))
        and (location := geocode_with_cache(venue))
    ]
