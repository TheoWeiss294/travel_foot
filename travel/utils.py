from data_classes import MatchGraph


def calc_incoming_degrees(graph: MatchGraph) -> list[int]:
    incoming_degrees = [0 for _ in range(len(graph))]
    for neighbors_dict in graph:
        for neighbour in neighbors_dict.keys():
            incoming_degrees[neighbour] += 1
    return incoming_degrees
