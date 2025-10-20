from data_classes import Match, MatchGraph
from .utils import (
    calc_incoming_degrees,
    days_between,
    dist_between,
    remove_subsequences,
)

Candidate = tuple[int, ...]


class TravelGraph:
    matches: list[Match]
    total_days: int
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
        paths: set[Candidate] = set()
        visited: set[Candidate] = set()

        def dfs(candidate: Candidate, days_left: int) -> bool:
            if not candidate or candidate in visited:
                return False

            last_match = candidate[-1]
            success = len(candidate) >= min_games
            found_extension = False

            for next_match, days in self.graph[last_match].items():
                if days <= days_left:
                    new_candidate = candidate + (next_match,)
                    if dfs(new_candidate, days_left - days):
                        found_extension = True
                else:
                    assert len(candidate) > 1
                    sub_candidate = candidate[1:]
                    if sub_candidate in visited:
                        continue
                    gap = self._days_between(candidate[0], candidate[1])
                    dfs(sub_candidate, days_left + gap)

            if success and not found_extension:
                paths.add(tuple(candidate))
            visited.add(candidate)
            return success or found_extension

        incoming_degrees = calc_incoming_degrees(self.graph)
        root_matches = [i for i in range(len(self.matches)) if incoming_degrees[i] == 0]

        for match_index in root_matches:
            dfs((match_index,), self.total_days - 1)

        paths = remove_subsequences(paths)
        match_paths = [[self.matches[m] for m in path] for path in paths]
        return sorted(match_paths, key=lambda path: path[0].date)

    def format_paths(self, schedule_options: list[list[Match]]) -> str:
        lines = []
        for option_idx, schedule in enumerate(schedule_options, start=1):
            lines.append(f"Option {option_idx}:")
            for gd in schedule:
                # matches_str = " | ".join(map(str, gd.matches))
                lines.append(f"  {gd.date.strftime('%Y-%m-%d')}: [{gd}]")
        return "\n".join(lines)

    def _days_between(self, i: int, j: int) -> int:
        return days_between(self.matches[i], self.matches[j])
