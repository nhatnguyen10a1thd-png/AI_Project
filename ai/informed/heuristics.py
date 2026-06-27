# ai/informed/heuristics.py

HEURISTIC_NAME = "sum_manhattan_nut_to_nearest_empty_hole"

def manhattan_distance(a, b):
    """Computes Manhattan distance between two coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def squirrel_heuristic(state):
    """
    Heuristic h(n): sum of Manhattan distances from each active squirrel nut
    to the nearest unfilled hole.

    AIMA mapping:
    - state: the current board configuration.
    - goal test: every squirrel has dropped its nut.
    - heuristic: distance guidance toward empty holes.

    This is a pragmatic guide for Squirrels Go Nuts. It has not been proven
    admissible or consistent for every sliding/blocking interaction, so A*
    optimality is guaranteed only on instances where the heuristic satisfies
    those conditions.
    """
    empty_holes = state.holes - state.filled_holes
    if not empty_holes:
        return 0
        
    total_distance = 0
    for pid, p in state.pieces.items():
        if p.type == "squirrel" and p.has_nut:
            nut_pos = p.nut_position()
            if nut_pos:
                # Find the nearest unfilled hole
                min_dist = min(manhattan_distance(nut_pos, hole) for hole in empty_holes)
                total_distance += min_dist
                
    return total_distance
