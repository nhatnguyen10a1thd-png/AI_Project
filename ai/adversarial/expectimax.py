# ai/adversarial/expectimax.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.search_result import SearchResult
from ai.utils import action_to_text, clone_state, safe_apply_action


def expectimax_solve(start_state, rules, max_depth=3, max_moves=10):
    """
    Expectimax from AIMA, adapted to MAX + CHANCE for Squirrels Go Nuts.

    MAX controls the squirrel moves.  CHANCE models a stochastic flower/blocker:
    it may stay still or move one legal step with normalized probabilities.
    This is not an active adversary; for an active blocker use Minimax or
    Alpha-Beta.
    """
    start_time = time.time()
    steps = [(0, f"Khởi tạo Expectimax: MAX=squirrel, CHANCE=flower stochastic, max_depth={max_depth}", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]
    reason = "max_moves"

    def get_max_actions(state):
        actions = []
        for piece_id, piece in state.pieces.items():
            if piece.type == "squirrel" and piece.movable:
                for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
                    if rules.can_move(state, piece_id, direction):
                        actions.append((piece_id, direction))
        return actions

    def get_flower_actions(state):
        if "flower" not in state.pieces:
            return []
        cloned = clone_state(state)
        cloned.pieces["flower"].movable = True
        actions = []
        for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
            if rules.can_move(cloned, "flower", direction):
                actions.append(("flower", direction))
        return actions

    def apply_flower_action(state, action):
        cloned = clone_state(state)
        cloned.pieces["flower"].movable = True
        next_state = safe_apply_action(cloned, rules, action)
        if "flower" in next_state.pieces:
            next_state.pieces["flower"].movable = False
        return next_state

    def chance_outcomes(state):
        flower_actions = get_flower_actions(state)
        if not flower_actions:
            return [(1.0, "flower_stays_or_absent", clone_state(state))]

        outcomes = [(0.5, "flower_stays", clone_state(state))]
        move_probability = 0.5 / len(flower_actions)
        for action in flower_actions:
            outcomes.append((move_probability, action_to_text(action), apply_flower_action(state, action)))

        total = sum(probability for probability, _, _ in outcomes)
        if total != 1.0:
            outcomes = [(probability / total, label, outcome_state) for probability, label, outcome_state in outcomes]
        return outcomes

    def utility(state):
        if state.is_goal():
            return 1000.0
        return -float(squirrel_heuristic(state))

    def expectimax_value(state, depth, node_type):
        visited_count[0] += 1

        if state.is_goal():
            value = utility(state)
            steps.append((step_num[0], f"{node_type.upper()} terminal goal depth={depth}, utility={value}", state))
            step_num[0] += 1
            return value, None

        if depth == 0:
            value = utility(state)
            steps.append((step_num[0], f"{node_type.upper()} cutoff depth=0, utility={value}", state))
            step_num[0] += 1
            return value, None

        if node_type == "max":
            actions = get_max_actions(state)
            if not actions:
                value = utility(state)
                steps.append((step_num[0], f"MAX không có action, utility={value}", state))
                step_num[0] += 1
                return value, None

            best_value = -float("inf")
            best_action = None
            steps.append((step_num[0], f"MAX node depth_remaining={depth}, actions={len(actions)}", state))
            step_num[0] += 1
            for action in actions:
                generated_count[0] += 1
                next_state = safe_apply_action(state, rules, action)
                value, _ = expectimax_value(next_state, depth - 1, "chance")
                steps.append((step_num[0], f"MAX xét {action_to_text(action)} -> expected value={value:.3f}", next_state))
                step_num[0] += 1
                if value > best_value:
                    best_value = value
                    best_action = action
            steps.append((step_num[0], f"MAX chọn {action_to_text(best_action)} vì expected value cao nhất={best_value:.3f}", state))
            step_num[0] += 1
            return best_value, best_action

        outcomes = chance_outcomes(state)
        probability_sum = sum(probability for probability, _, _ in outcomes)
        expected_value = 0.0
        steps.append(
            (
                step_num[0],
                f"CHANCE node depth_remaining={depth}, outcomes={len(outcomes)}, probability_sum={probability_sum:.3f}",
                state,
            )
        )
        step_num[0] += 1
        for probability, label, outcome_state in outcomes:
            generated_count[0] += 1
            value, _ = expectimax_value(outcome_state, depth - 1, "max")
            expected_value += probability * value
            steps.append(
                (
                    step_num[0],
                    f"CHANCE outcome {label}: p={probability:.3f}, value={value:.3f}, partial_E={expected_value:.3f}",
                    outcome_state,
                )
            )
            step_num[0] += 1
        return expected_value, None

    current_state = start_state
    path = []

    for move_index in range(1, max_moves + 1):
        if current_state.is_goal():
            reason = "goal_found"
            break

        value, action = expectimax_value(current_state, max_depth, "max")
        if action is None:
            reason = "no_max_action"
            steps.append((step_num[0], "MAX không có action để đi", current_state))
            step_num[0] += 1
            break

        current_state = safe_apply_action(current_state, rules, action)
        path.append(action)
        steps.append((step_num[0], f"Simulation MAX chọn {action_to_text(action)} với expected={value:.3f}", current_state))
        step_num[0] += 1

        if current_state.is_goal():
            reason = "goal_found"
            break

        outcomes = chance_outcomes(current_state)
        probability, label, outcome_state = outcomes[0]
        current_state = outcome_state
        steps.append(
            (
                step_num[0],
                f"Simulation CHANCE chọn deterministic outcome đầu tiên: {label}, p={probability:.3f}",
                current_state,
            )
        )
        step_num[0] += 1

    solved = current_state.is_goal()
    if solved:
        reason = "goal_found"

    return SearchResult(
        algorithm="Expectimax",
        solved=solved,
        path=path if solved else [],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "chance_model": "Flower stays with p=0.5 or moves one legal direction sharing p=0.5; if no action, p=1 stay.",
            "max_depth": max_depth,
            "max_moves": max_moves,
            "evaluation_name": f"goal=1000, non_terminal=-{HEURISTIC_NAME}",
            "reason": reason,
        },
    )
