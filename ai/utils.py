# ai/utils.py

class SearchNode:
    """Represents a node in the search tree."""
    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0):
        self.state = state          # GameState object
        self.parent = parent        # Parent SearchNode
        self.action = action        # Action that led to this state (piece_id, direction)
        self.path_cost = path_cost  # Cumulative path cost (g)
        self.depth = depth          # Depth in the search tree

    def __lt__(self, other):
        # We need this for heapq in case f-scores are equal
        return self.path_cost < other.path_cost

def reconstruct_path(node):
    """Reconstructs the path of actions and states from start to the given node."""
    actions = []
    states = []
    curr = node
    while curr:
        states.append(curr.state)
        if curr.action:
            actions.append(curr.action)
        curr = curr.parent
    return actions[::-1], states[::-1]
