from venues import haversine_distance
from data_classes import Match, Matchday, MatchPath, MatchGraph
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

    def find_paths(self, min_games: int) -> str:
        paths: list[MatchPath] = []
        incoming_degrees = calc_incoming_degrees(self.graph)
        root_matches = [i for i in range(len(self.matches)) if incoming_degrees[i] == 0]

        for match_index in root_matches:
            self.find_path_with_candidate(
                [Matchday(self.matches[match_index].date, set([match_index]))],
                min_games,
                self.total_days - 1,
                paths,
            )

        sorted_paths = sorted(paths, key=lambda path: path[0].date)
        return self.format_paths(sorted_paths)

    def find_path_with_candidate(
        self,
        candidate: MatchPath,
        min_games: int,
        days_left: int,
        output: list[MatchPath],
    ) -> bool:
        if not candidate:
            return False
        last_matchday = candidate[-1]
        success = len(candidate) >= min_games
        found_better = False

        matches = last_matchday.matches
        date = last_matchday.date
        first_hops = set(n for match in matches for n in self.graph[match].keys())
        second_hops = set(n for hop in first_hops for n in self.graph[hop].keys())
        candidates = [first_hops] if first_hops else []
        for second in second_hops:
            if (self.matches[second].date - date).days > days_left:
                continue
            new_candidates: list[set[int]] = []
            for matchday in candidates:
                if second in matchday:
                    matchday.remove(second)
                if valid_stops := set(
                    match for match in matchday if second in self.graph[match]
                ):
                    new_candidates.append(valid_stops)
                if remaining := matchday - valid_stops:
                    new_candidates.append(remaining)
            candidates = new_candidates

        for next_matches in candidates:
            found_better = True
            matchdays = self._group_by_days(next_matches)
            for matchday in matchdays:
                self.find_path_with_candidate(
                    candidate + [matchday],
                    min_games,
                    days_left=days_left - (matchday.date - date).days,
                    output=output,
                )

        if success and not found_better:
            output.append(candidate)
        return success or found_better

    def _group_by_days(self, matches: set[int]) -> list[Matchday]:
        matchdays_dict = {}
        for match_index in matches:
            date = self.matches[match_index].date
            if date not in matchdays_dict:
                matchdays_dict[date] = set()
            matchdays_dict[date].add(match_index)
        return [Matchday(date, matches) for date, matches in matchdays_dict.items()]

    def format_paths(self, schedule_options: list[MatchPath]) -> str:
        lines = []
        for option_idx, schedule in enumerate(schedule_options, start=1):
            lines.append(f"Option {option_idx}:")
            for gd in schedule:
                matches = " | ".join(str(self.matches[m]) for m in gd.matches)
                lines.append(f"  {gd.date.strftime('%Y-%m-%d')}: [{matches}]")
        return "\n".join(lines)
