# ai/utils.py
import copy


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


def clone_state(state):
    """Return an isolated copy of a GameState-like object."""
    if hasattr(state, "clone"):
        return state.clone()
    return copy.deepcopy(state)


def safe_apply_action(state, rules, action):
    """
    Apply an action on a cloned state and return an isolated successor state.

    BoardRules.apply_action currently returns a fresh GameState, but search
    algorithms should not rely on that implementation detail.  This helper
    protects the parent node even if a future rules object mutates the state it
    receives or returns None after mutating in place.
    """
    working_state = clone_state(state)
    result = rules.apply_action(working_state, action)
    if result is None:
        result = working_state
    return clone_state(result)


def action_to_text(action):
    """Human-readable action label for logs."""
    if action is None:
        return "PASS"
    piece_id, direction = action
    return f"{piece_id} {direction}"
