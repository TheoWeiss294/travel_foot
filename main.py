from datetime import datetime, timezone

from venues import geocode_with_cache
from connectors import football_data
from travel import travel


TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def main():
    fixtures = football_data.get_champions_league_fixtures(
        datetime(2025, 9, 1), datetime(2025, 10, 1)
    )
    data = football_data.get_competition_teams(football_data.LeagueId.CHAMPIONS_LEAGUE)
    home_grounds = {
        team["name"]: team["venue"] for team in data["teams"] if team["venue"]
    }
    matches = [
        travel.Match(
            f["homeTeam"]["name"],
            f["awayTeam"]["name"],
            datetime.strptime(f["utcDate"], TIME_FORMAT).replace(tzinfo=timezone.utc),
            location,
        )
        for f in fixtures["matches"]
        if (venue := f.get("venue", home_grounds.get(f["homeTeam"]["name"])))
        and (location := geocode_with_cache(venue))
    ]
    graph = travel.TravelGraph(matches, max_dist=50, max_days=4)
    paths = graph.find_paths(min_games=2)
    print(paths)


if __name__ == "__main__":
    main()
