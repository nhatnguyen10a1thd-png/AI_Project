# ai/adversarial/expectimax.py
import time

from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult


def expectimax_solve(start_state, rules, max_depth=3, max_moves=10):
    """
    Expectimax demo.

    MAX chooses squirrel moves. Chance nodes model a stochastic blocker: the
    flower may stay still or move one legal step in a random direction.
    """
    start_time = time.time()
    steps = [(0, "Start Expectimax (MAX squirrels, CHANCE flower)", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]

    def get_max_actions(state):
        actions = []
        for pid, piece in state.pieces.items():
            if piece.type == "squirrel" and piece.movable:
                for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
                    if rules.can_move(state, pid, direction):
                        actions.append((pid, direction))
        return actions

    def get_flower_actions(state):
        actions = []
        if "flower" not in state.pieces:
            return actions

        cloned = state.clone()
        cloned.pieces["flower"].movable = True
        for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
            if rules.can_move(cloned, "flower", direction):
                actions.append(("flower", direction))
        return actions

    def apply_flower_action(state, action):
        cloned = state.clone()
        cloned.pieces["flower"].movable = True
        next_state = rules.apply_action(cloned, action)
        if "flower" in next_state.pieces:
            next_state.pieces["flower"].movable = False
        return next_state

    def chance_outcomes(state):
        flower_actions = get_flower_actions(state)
        if not flower_actions:
            return [(1.0, state)]

        outcomes = [(0.5, state)]
        move_probability = 0.5 / len(flower_actions)
        for action in flower_actions:
            outcomes.append((move_probability, apply_flower_action(state, action)))
        return outcomes

    def utility(state):
        if state.is_goal():
            return 1000.0
        return -float(squirrel_heuristic(state))

    def expectimax_value(state, depth, node_type):
        visited_count[0] += 1

        if depth == 0 or state.is_goal():
            return utility(state), None

        if node_type == "max":
            actions = get_max_actions(state)
            if not actions:
                return utility(state), None

            best_value = -float("inf")
            best_action = None
            for action in actions:
                generated_count[0] += 1
                next_state = rules.apply_action(state, action)
                value, _ = expectimax_value(next_state, depth - 1, "chance")
                if value > best_value:
                    best_value = value
                    best_action = action
            return best_value, best_action

        expected_value = 0.0
        for probability, outcome_state in chance_outcomes(state):
            generated_count[0] += 1
            value, _ = expectimax_value(outcome_state, depth - 1, "max")
            expected_value += probability * value
        return expected_value, None

    current_state = start_state
    path = []

    for move_idx in range(max_moves):
        if current_state.is_goal():
            break

        value, action = expectimax_value(current_state, max_depth, "max")
        if action is None:
            break

        current_state = rules.apply_action(current_state, action)
        path.append(action)
        steps.append(
            (
                step_num[0],
                f"MAX move {move_idx + 1}: {action[0]} {action[1]} (expected={value:.2f})",
                current_state,
            )
        )
        step_num[0] += 1

    solved = current_state.is_goal()

    return SearchResult(
        algorithm="Expectimax",
        solved=solved,
        path=path if solved else [],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
    )
