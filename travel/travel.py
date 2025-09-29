from data_classes import Match, MatchGraph
from .utils import (
    calc_incoming_degrees,
    days_between,
    dist_between,
    remove_subsequences,
)


class TravelGraph:
    total_days = int
    matches = list[Match]
    graph: list[dict[int, int]]

    def __init__(self, matches: list[Match], max_dist: int, max_days: int):
        self.matches: list[Match] = sorted(matches, key=lambda m: m.date)
        self.total_days: int = max_days
        self.graph: MatchGraph = self._init_graph(max_dist)

    def _init_graph(self, max_dist: int) -> MatchGraph:
        n = len(self.matches)
        return [
            {
                j: days
                for j in range(i + 1, n)
                if (days := days_between(match, self.matches[j]))
                and (0 < days < self.total_days)
                and (dist_between(match, self.matches[j]) < max_dist)
            }
            for i, match in enumerate(self.matches)
        ]

    def find_paths(self, min_games: int) -> list[list[Match]]:
        paths: set[tuple[int]] = set()
        incoming_degrees = calc_incoming_degrees(self.graph)
        root_matches = [i for i in range(len(self.matches)) if incoming_degrees[i] == 0]

        for match_index in root_matches:
            self.find_path_with_candidate(
                [match_index], min_games, self.total_days - 1, paths, set()
            )
        paths = remove_subsequences(paths)
        match_paths = [[self.matches[m] for m in path] for path in paths]

        return sorted(match_paths, key=lambda path: path[0].date)

    def find_path_with_candidate(
        self,
        candidate: list[int],
        min_games: int,
        days_left: int,
        output: set[tuple[int]],
        visited: set[int],
    ) -> bool:
        if not candidate:
            return False
        last_match = candidate[-1]
        if len(candidate) == 1 and last_match in visited:
            return False
        success = len(candidate) >= min_games
        found_better = False

        for next_match, days in self.graph[last_match].items():
            if days <= days_left:
                found_better = (
                    self.find_path_with_candidate(
                        candidate + [next_match],
                        min_games,
                        days_left - days,
                        output,
                        visited,
                    )
                    or found_better
                )
            else:
                self.find_path_with_candidate(
                    [candidate[1]], min_games, self.total_days - 1, output, visited
                )
        if success and not found_better:
            output.add(tuple(candidate))
        if len(candidate) == 1:
            visited.add(last_match)
        return success or found_better

    def format_paths(self, schedule_options: list[list[Match]]) -> str:
        lines = []
        for option_idx, schedule in enumerate(schedule_options, start=1):
            lines.append(f"Option {option_idx}:")
            for gd in schedule:
                # matches_str = " | ".join(map(str, gd.matches))
                lines.append(f"  {gd.date.strftime('%Y-%m-%d')}: [{gd}]")
        return "\n".join(lines)
