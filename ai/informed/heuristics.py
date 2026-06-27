# ai/informed/heuristics.py

def manhattan_distance(a, b):
    """Computes Manhattan distance between two coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def squirrel_heuristic(state):
    """
    Heuristic function h(n): Sum of Manhattan distances from each active squirrel's nut
    to the nearest unfilled hole on the board.
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
