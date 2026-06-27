# ai/adversarial/minimax.py
import time
from ai.search_result import SearchResult
from ai.informed.heuristics import squirrel_heuristic


def minimax_solve(start_state, rules, max_depth=3):
    """
    Solves/Simulates the puzzle using Minimax Search (Adversarial Mode).
    MAX controls the squirrels (trying to minimize heuristic / reach goal).
    MIN controls the flower block (trying to maximize heuristic / block MAX).

    Bug fix: no longer mutates flower.movable on shared state objects.
    Instead, we use rules.apply_action on a cloned state with flower temporarily enabled.
    """
    start_time = time.time()
    steps = [(0, "Bắt đầu Minimax (MAX = Sóc, MIN = Hoa)", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]

    def get_max_actions(state):
        """Squirrel actions only."""
        actions = []
        for pid, p in state.pieces.items():
            if p.type == "squirrel" and p.movable:
                for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    if rules.can_move(state, pid, d):
                        actions.append((pid, d))
        return actions

    def get_min_actions(state):
        """
        Flower actions. Uses a CLONED state so original is not mutated.
        Returns list of (action, resulting_state) pairs.
        """
        result_actions = []
        if "flower" in state.pieces:
            # Clone and temporarily make flower movable
            cloned = state.clone()
            cloned.pieces["flower"].movable = True
            for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
                if rules.can_move(cloned, "flower", d):
                    next_st = rules.apply_action(cloned, ("flower", d))
                    # Restore flower to immovable in the resulting state
                    if "flower" in next_st.pieces:
                        next_st.pieces["flower"].movable = False
                    result_actions.append(("flower", d))
        if not result_actions:
            result_actions.append(None)  # Pass turn
        return result_actions

    def apply_min_action(state, action):
        """Safely apply a flower action on a cloned state."""
        if action is None:
            return state
        cloned = state.clone()
        cloned.pieces["flower"].movable = True
        next_st = rules.apply_action(cloned, action)
        if "flower" in next_st.pieces:
            next_st.pieces["flower"].movable = False
        return next_st

    def utility(state):
        if state.is_goal():
            return 1000
        return -squirrel_heuristic(state)

    def minimax_decision(state, depth, is_max_turn):
        visited_count[0] += 1

        if depth == 0 or state.is_goal():
            return utility(state), None

        if is_max_turn:
            best_val = -float('inf')
            best_act = None
            actions = get_max_actions(state)
            if not actions:
                return utility(state), None

            for act in actions:
                generated_count[0] += 1
                next_state = rules.apply_action(state, act)
                val, _ = minimax_decision(next_state, depth - 1, False)
                if val > best_val:
                    best_val = val
                    best_act = act
            return best_val, best_act
        else:
            best_val = float('inf')
            best_act = None
            actions = get_min_actions(state)

            for act in actions:
                generated_count[0] += 1
                if act is None:
                    val, _ = minimax_decision(state, depth - 1, True)
                else:
                    next_state = apply_min_action(state, act)
                    val, _ = minimax_decision(next_state, depth - 1, True)

                if val < best_val:
                    best_val = val
                    best_act = act
            return best_val, best_act

    # Simulate play between MAX and MIN
    current_state = start_state
    sim_path = []

    for move_idx in range(10):
        if current_state.is_goal():
            break

        # MAX Turn: Squirrel moves
        _, best_max_act = minimax_decision(current_state, max_depth, True)
        if not best_max_act:
            break
        current_state = rules.apply_action(current_state, best_max_act)
        sim_path.append(best_max_act)
        steps.append((step_num[0], f"MAX: Sóc {best_max_act[0]} trượt {best_max_act[1]}", current_state))
        step_num[0] += 1

        if current_state.is_goal():
            break

        # MIN Turn: Flower moves
        _, best_min_act = minimax_decision(current_state, max_depth, False)
        if best_min_act:
            next_state = apply_min_action(current_state, best_min_act)
            current_state = next_state
            sim_path.append(best_min_act)
            steps.append((step_num[0], f"MIN: Hoa cản {best_min_act[0]} {best_min_act[1]}", current_state))
            step_num[0] += 1

    solved = current_state.is_goal()

    return SearchResult(
        algorithm="Minimax",
        solved=solved,
        path=sim_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps
    )
