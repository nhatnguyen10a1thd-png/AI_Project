# ai/informed/heuristics.py
from itertools import combinations, permutations

from core.constants import BOARD_SIZE


HEURISTIC_NAME = "min_assignment_manhattan_nuts_to_empty_holes"

def manhattan_distance(a, b):
    """Computes Manhattan distance between two coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def squirrel_heuristic(state):
    """
    Heuristic h(n): minimum total Manhattan assignment from active squirrel
    nuts to distinct unfilled holes.

    AIMA mapping:
    - state: the current board configuration.
    - goal test: every squirrel has dropped its nut.
    - heuristic: distance guidance toward a one-nut-per-hole completion.

    This is stronger than independently choosing the nearest hole for each nut
    because it avoids assigning two active nuts to the same empty hole. It still
    ignores blockers and piece shapes, so it is a pragmatic guide rather than a
    proof of admissibility/consistency for every puzzle variant.
    """
    active_nuts = []
    for p in state.pieces.values():
        if p.type == "squirrel" and p.has_nut:
            nut_pos = p.nut_position()
            if nut_pos is not None:
                active_nuts.append(nut_pos)

    if not active_nuts:
        return 0

    empty_holes = list(state.holes - state.filled_holes)
    if not empty_holes:
        return len(active_nuts) * BOARD_SIZE

    if len(empty_holes) < len(active_nuts):
        nearest_sum = sum(
            min(manhattan_distance(nut_pos, hole) for hole in empty_holes)
            for nut_pos in active_nuts
        )
        missing_hole_penalty = (len(active_nuts) - len(empty_holes)) * BOARD_SIZE
        return nearest_sum + missing_hole_penalty

    best_cost = float("inf")
    for hole_subset in combinations(empty_holes, len(active_nuts)):
        for assigned_holes in permutations(hole_subset):
            cost = sum(
                manhattan_distance(nut_pos, hole)
                for nut_pos, hole in zip(active_nuts, assigned_holes)
            )
            best_cost = min(best_cost, cost)

    return best_cost
