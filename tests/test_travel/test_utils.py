from travel import utils


def test__all_equivalent_paths__sanity() -> None:
    equivalence_dict = {1: [1, 2], 3: [3, 4], 5: [5]}
    paths = set([(1, 3, 5)])
    expected = set([(1, 3, 5), (1, 4, 5), (2, 3, 5), (2, 4, 5)])
    assert utils.all_equivalent_paths(paths, equivalence_dict) == expected
