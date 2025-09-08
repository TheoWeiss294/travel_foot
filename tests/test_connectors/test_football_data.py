from datetime import datetime, timedelta

from connectors import football_data


def test_get_upcoming_fixtures__sanity():
    today = datetime(2025, 9, 1)
    data = football_data.get_upcoming_fixtures(
        football_data.FixturesParams(
            football_data.LeagueId.CHAMPIONS_LEAGUE, today, today + timedelta(days=30)
        )
    )
    assert data
    assert data["matches"]
    assert all(match["utcDate"] for match in data["matches"])
    assert all(match["homeTeam"] for match in data["matches"])
    assert all(match["awayTeam"] for match in data["matches"])


def test_get_champions_league_fixtures__sanity():
    today = datetime(2025, 9, 1)
    data = football_data.get_champions_league_fixtures(
        today, today + timedelta(days=30)
    )

    assert data
    assert data["matches"]
    assert all(match["utcDate"] for match in data["matches"])
    assert all(match["homeTeam"] for match in data["matches"])
    assert all(match["awayTeam"] for match in data["matches"])


def test_get_competition_teams__sanity():
    threshold = 5  # TODO: decrease threshold

    data = football_data.get_competition_teams(football_data.LeagueId.CHAMPIONS_LEAGUE)
    assert data
    assert data["teams"]
    missing_venue = {}
    for team in data["teams"]:
        if not team["venue"]:
            missing_venue[team["name"]] = team["venue"]

    assert len(missing_venue) < threshold, "Some clubs are missing venues"
