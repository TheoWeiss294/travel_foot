import argparse
from datetime import datetime, timezone, timedelta

from travel import match, travel


def run(min_games: int, max_days: int, max_dist: float, days_ahead: int) -> None:
    today = datetime.now(timezone.utc)
    matches = match.get_all_matches(today, today + timedelta(days=days_ahead))
    graph = travel.TravelGraph(matches, max_dist=max_dist, max_days=max_days)
    paths = graph.find_paths(min_games=min_games)
    print(paths)


def main():
    parser = argparse.ArgumentParser(
        description="Find relative sports events in time and space"
    )
    parser.add_argument(
        "--min-games", type=int, default=2, help="Minimum number of games in a path"
    )
    parser.add_argument(
        "--max-days", type=int, default=4, help="Maximum days between games"
    )
    parser.add_argument(
        "--max-dist",
        type=float,
        default=50.0,
        help="Maximum distance (km) between venues",
    )
    parser.add_argument(
        "--days-ahead",
        type=int,
        default=30,
        help="Number of days to look ahead for fixtures",
    )

    args = parser.parse_args()
    run(
        min_games=args.min_games,
        max_days=args.max_days,
        max_dist=args.max_dist,
        days_ahead=args.days_ahead,
    )


if __name__ == "__main__":
    main()
