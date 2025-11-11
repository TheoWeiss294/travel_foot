from typing import Iterable
from datetime import datetime
from itertools import product

from venues import haversine_distance
from data_classes import Match, EquivalenceDict, Candidate


def days_between(m1: Match, m2: Match) -> int:
    return days_between_dates(m1.date, m2.date)


def days_between_dates(d1: datetime, d2: datetime) -> int:
    return (d2.date() - d1.date()).days


def dist_between(m1: Match, m2: Match) -> float:
    return haversine_distance(m1.location, m2.location)


def remove_subsequences(tuples_set: set[Candidate]) -> set[Candidate]:
    result = set()
    tuples_list = sorted(tuples_set, key=len, reverse=True)
    for tpl in tuples_list:
        if any(is_subsequence(tpl, other) for other in result):
            continue
        result.add(tpl)
    return result


def is_subsequence(list1: Iterable[int], list2: Iterable[int]) -> bool:
    it = iter(list2)
    return all(x in it for x in list1)


def all_equivalent_paths(
    paths: set[Candidate], equiv_dict: EquivalenceDict
) -> set[Candidate]:
    return {
        tuple(new_path)
        for path in paths
        for new_path in product(*(equiv_dict[match] for match in path))
    }
