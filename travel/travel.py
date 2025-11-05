from data_classes import Match, MatchGraph, NodeAdjacency
from .utils import days_between, dist_between, remove_subsequences

Candidate = tuple[int, ...]


class TravelGraph:
    matches: list[Match]
    total_days: int
    graph: MatchGraph

    def __init__(self, matches: list[Match], max_dist: int, max_days: int):
        self.matches: list[Match] = sorted(matches, key=lambda m: m.date)
        self.total_days: int = max_days
        self._init_graph(max_dist)

    def _init_graph(self, max_dist: int) -> None:
        n = len(self.matches)
        graph: list[NodeAdjacency] = [NodeAdjacency({}, {}) for _ in range(n)]

        for i, match_i in enumerate(self.matches):
            for j in range(i + 1, n):
                match_j = self.matches[j]
                days = days_between(match_i, match_j)

                if days >= self.total_days:
                    break
                if days == 0:
                    continue
                # TODO: memoization
                if dist_between(match_i, match_j) > max_dist:
                    continue

                graph[i].outgoing[j] = days
                graph[j].incoming[i] = days

        self.graph = graph

    def find_paths(self, min_games: int) -> list[list[Match]]:
        paths: set[Candidate] = set()
        visited: set[Candidate] = set()

        def dfs(candidate: Candidate, days_left: int) -> bool:
            if not candidate or candidate in visited:
                return False

            last_match = candidate[-1]
            success = len(candidate) >= min_games
            found_extension = False

            for next_match, days in self.graph[last_match].outgoing.items():
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

        root_matches = [i for i, node in enumerate(self.graph) if not node.incoming]
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

    def _equivalent_nodes(self, i: int, j: int) -> bool:
        return (
            self._days_between(i, j) == 0
            and self.graph[i].incoming == self.graph[j].incoming
            and self.graph[i].outgoing == self.graph[j].outgoing
        )
