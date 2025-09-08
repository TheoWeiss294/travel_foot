from typing import NamedTuple
from datetime import datetime
from venues import Location, haversine_distance


class Match(NamedTuple):
    home_team: str
    away_team: str
    date: datetime
    location: Location


class TravelGraph:
    total_days = int
    matches = list[Match]
    graph: list[dict[int, int]]

    def __init__(self, matches: list[Match], max_dist: int, max_days: int):
        self.matches = sorted(matches, key=lambda m: m.date)
        self.total_days = max_days
        self.graph = self._init_graph(max_dist)

    def _init_graph(self, max_dist: int) -> list[dict[int, int]]:
        n = len(self.matches)
        return [
            {
                j: days
                for j in range(i + 1, n)
                if (days := (self.matches[j].date - match.date).days)
                and (days < self.total_days)
                and (
                    haversine_distance(match.location, self.matches[j].location)
                    < max_dist
                )
            }
            for i, match in enumerate(self.matches)
        ]

    def find_paths(self, min_games: int) -> list[list[Match]]:
        paths = []
        incoming_degrees = [0 for _ in range(len(self.matches))]
        for neighbors_dict in self.graph:
            for neighbour in neighbors_dict.keys():
                incoming_degrees[neighbour] += 1

        root_matches = [i for i in range(len(self.matches)) if incoming_degrees[i] == 0]
        for match_index in root_matches:
            self.find_path_with_candidate(
                [match_index], min_games, self.total_days - 1, paths
            )

        # TODO: join similar paths
        match_pathes: list[list[Match]] = [
            [self.matches[i] for i in path] for path in paths
        ]
        return sorted(match_pathes, key=lambda path: path[0].date)

    def find_path_with_candidate(
        self,
        candidate: list[int],
        min_games: int,
        days_left: int,
        output: list[list[int]],
    ) -> bool:
        if not candidate:
            return False
        last_match = candidate[-1]
        success = len(candidate) >= min_games
        found_better = False

        for next_match, days_between in self.graph[last_match].items():
            if days_between <= days_left:
                found_better = True
                self.find_path_with_candidate(
                    candidate + [next_match],
                    min_games,
                    days_left - days_between,
                    output,
                )
            elif len(candidate) > 1:
                first = candidate[0]
                second = candidate[1]
                skip_days = (self.matches[second].date - self.matches[first].date).days
                self.find_path_with_candidate(
                    candidate[1:] + [next_match],
                    min_games,
                    days_left + skip_days,
                    output,
                )

        if success and not found_better:
            output.append(candidate)
        return success or found_better
