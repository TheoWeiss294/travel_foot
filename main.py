from datetime import datetime

from venues import Location, geocode_with_cache
from connectors import football_data, open_street_map
from travel import travel


def main():
    fixtures = football_data.get_champions_league_fixtures(
        datetime(2025, 9, 1), datetime(2025, 10, 1)
    )
    teams = football_data.get_competition_teams(football_data.LeagueId.CHAMPIONS_LEAGUE)
    home_grounds = {team["name"]: team["venue"] for team in teams if team["venue"]}
    matches = [
        travel.Match(f["homeTeam"], f["awayTeam"], datetime(f["utcDate"]), location)
        for f in fixtures
        if (location := geocode_with_cache(f["venue"] or home_grounds[f["homeTeam"]]))
    ]
    graph = travel.TravelGraph(matches, max_dist=50, max_days=4)
    paths = graph.find_paths(min_games=2)
    print(paths)


if __name__ == "__main__":
    main()
