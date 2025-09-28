from venues import haversine_distance
from data_classes import Match, MatchGraph
from .utils import calc_incoming_degrees


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
        paths: list[list[Match]] = []
        incoming_degrees = calc_incoming_degrees(self.graph)
        root_matches = [i for i in range(len(self.matches)) if incoming_degrees[i] == 0]

        for match_index in root_matches:
            self.find_path_with_candidate(
                [match_index], min_games, self.total_days - 1, paths
            )

        return sorted(paths, key=lambda path: path[0].date)

    def find_path_with_candidate(
        self,
        candidate: list[int],
        min_games: int,
        days_left: int,
        output: list[list[Match]],
    ) -> bool:
        if not candidate:
            return False
        last_match = candidate[-1]
        success = len(candidate) >= min_games
        found_better = False

        for next_match, days in self.graph[last_match].items():
            if days <= days_left:
                found_better = self.find_path_with_candidate(
                    candidate + [next_match], min_games, days_left - days, output
                )
            else:
                first, second = candidate[:2]
                removed = (self.matches[second].date - self.matches[first].date).days
                self.find_path_with_candidate(
                    candidate[1:], min_games, days_left + removed, output
                )
        if success and not found_better:
            output.append([self.matches[m] for m in candidate])
        return success or found_better

    def format_paths(self, schedule_options: list[list[Match]]) -> str:
        lines = []
        for option_idx, schedule in enumerate(schedule_options, start=1):
            lines.append(f"Option {option_idx}:")
            for gd in schedule:
                # matches_str = " | ".join(map(str, gd.matches))
                lines.append(f"  {gd.date.strftime('%Y-%m-%d')}: [{gd}]")
        return "\n".join(lines)
