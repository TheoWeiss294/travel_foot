from typing import TypeAlias
from collections import defaultdict
from datetime import date

from data_classes import (
    Match,
    MatchGraph,
    NodeAdjacency,
    Candidate,
    EquivalenceDict,
    WeightedAdjacencyDict,
)
from .utils import days_between, dist_between, all_equivalent_paths

AdjacencyTuple: TypeAlias = tuple[tuple[int, int], ...]
EquivalenceKey: TypeAlias = tuple[date, int, AdjacencyTuple, AdjacencyTuple]


class TravelGraph:
    matches: list[Match]
    total_days: int
    graph: MatchGraph
    equiv_dict: EquivalenceDict

    def __init__(self, matches: list[Match], max_dist: int, max_days: int):
        self.matches: list[Match] = sorted(matches, key=lambda m: m.date)
        self.total_days: int = max_days
        self._init_graph(max_dist)
        self.equiv_dict = {min(group): group for group in self.group_equivalent_nodes()}

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

    def group_equivalent_nodes(self) -> list[list[int]]:
        groups: dict[EquivalenceKey, list[int]] = defaultdict(list)
        for i in range(len(self.matches)):
            groups[self._equivalence_key(i)].append(i)
        return list(groups.values())

    def find_paths(self, min_games: int) -> list[list[Match]]:
        paths: set[Candidate] = set()
        visited: set[Candidate] = set()
        sparse_graph = self._sparse_graph()

        def dfs(candidate: Candidate, days_left: int) -> bool:
            if (
                not candidate
                or candidate in visited
                or (candidate[0], candidate[-1]) in visited
            ):
                return False

            if days_left < 0:
                gap = self._days_between(candidate[0], candidate[1])
                return dfs(candidate[1:], days_left + gap)

            last_match = candidate[-1]
            success = len(candidate) >= min_games
            found_extension = False

            for next_match, days in sparse_graph[last_match].items():
                if days <= days_left:
                    new_candidate = candidate + (next_match,)
                    if dfs(new_candidate, days_left - days):
                        found_extension = True
                else:
                    assert len(candidate) > 1
                    sub_candidate = candidate[1:] + (next_match,)
                    if sub_candidate in visited:
                        continue
                    gap = self._days_between(candidate[0], candidate[1])
                    dfs(sub_candidate, days_left - days + gap)

            if success and not found_extension:
                paths.add(tuple(candidate))
            visited.add(candidate)
            visited.add((candidate[0], candidate[-1]))
            return success or found_extension

        root_matches = [x for x in sparse_graph.keys() if not self.graph[x].incoming]
        for match_index in root_matches:
            dfs((match_index,), self.total_days - 1)

        paths = all_equivalent_paths(paths, self.equiv_dict)
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

    def _equivalence_key(self, i: int) -> EquivalenceKey:
        incoming = tuple(self.graph[i].incoming.items())
        outgoing = tuple(self.graph[i].outgoing.items())
        isolated_key = i if not (incoming or outgoing) else -1
        return (self.matches[i].date.date(), isolated_key, incoming, outgoing)

    def _sparse_graph(self) -> dict[int, WeightedAdjacencyDict]:
        return {
            node: {
                neighbour: weight
                for neighbour, weight in self.graph[node].outgoing.items()
                if neighbour in self.equiv_dict.keys()
            }
            for node in self.equiv_dict.keys()
        }
