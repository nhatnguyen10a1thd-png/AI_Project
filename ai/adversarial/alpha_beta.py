# ai/adversarial/alpha_beta.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.search_result import SearchResult
from ai.utils import action_to_text, clone_state, safe_apply_action


def alphabeta_solve(start_state, rules, max_depth=3, max_moves=10, move_ordering=False):
    """
    Alpha-Beta pruning for depth-limited heuristic Minimax.

    The game mapping matches minimax_solve: MAX controls squirrels, MIN controls
    the flower blocker, terminal goal has high utility, and depth cutoffs use
    -squirrel_heuristic.  With move_ordering=False, action order matches
    Minimax so the chosen move is comparable at the same depth/evaluation.
    """
    start_time = time.time()
    steps = [(0, f"Khởi tạo Alpha-Beta: max_depth={max_depth}, move_ordering={move_ordering}", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]
    pruned_count = [0]
    reason = "max_moves"
    evaluation_name = f"goal=1000, non_terminal=-{HEURISTIC_NAME}"

    def get_max_actions(state):
        actions = []
        for piece_id, piece in state.pieces.items():
            if piece.type == "squirrel" and piece.movable:
                for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
                    if rules.can_move(state, piece_id, direction):
                        actions.append((piece_id, direction))
        if move_ordering:
            actions.sort(key=lambda action: squirrel_heuristic(safe_apply_action(state, rules, action)))
        return actions

    def get_min_actions(state):
        actions = []
        if "flower" in state.pieces:
            cloned = clone_state(state)
            cloned.pieces["flower"].movable = True
            for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
                if rules.can_move(cloned, "flower", direction):
                    actions.append(("flower", direction))
        if move_ordering:
            actions.sort(key=lambda action: squirrel_heuristic(apply_min_action(state, action)), reverse=True)
        if not actions:
            return [None]
        return actions

    def apply_min_action(state, action):
        if action is None:
            return clone_state(state)
        cloned = clone_state(state)
        cloned.pieces["flower"].movable = True
        next_state = safe_apply_action(cloned, rules, action)
        if "flower" in next_state.pieces:
            next_state.pieces["flower"].movable = False
        return next_state

    def utility(state):
        if state.is_goal():
            return 1000.0
        return -float(squirrel_heuristic(state))

    def alphabeta(state, depth, alpha, beta, is_max_turn):
        visited_count[0] += 1
        role = "MAX" if is_max_turn else "MIN"

        if state.is_goal():
            value = utility(state)
            steps.append((step_num[0], f"{role} terminal goal depth={depth}, utility={value}", state))
            step_num[0] += 1
            return value, None

        if depth == 0:
            value = utility(state)
            steps.append((step_num[0], f"{role} cutoff depth=0, utility={value}", state))
            step_num[0] += 1
            return value, None

        actions = get_max_actions(state) if is_max_turn else get_min_actions(state)
        if not actions:
            value = utility(state)
            steps.append((step_num[0], f"{role} không có action, utility={value}", state))
            step_num[0] += 1
            return value, None

        steps.append(
            (
                step_num[0],
                f"{role} node depth_remaining={depth}, alpha={alpha}, beta={beta}, actions={len(actions)}",
                state,
            )
        )
        step_num[0] += 1

        if is_max_turn:
            best_value = -float("inf")
            best_action = None
            for index, action in enumerate(actions):
                generated_count[0] += 1
                next_state = safe_apply_action(state, rules, action)
                value, _ = alphabeta(next_state, depth - 1, alpha, beta, False)
                old_alpha = alpha
                if value > best_value:
                    best_value = value
                    best_action = action
                alpha = max(alpha, best_value)
                steps.append(
                    (
                        step_num[0],
                        (
                            f"MAX xét {action_to_text(action)} -> value={value}, "
                            f"alpha {old_alpha}->{alpha}, beta={beta}"
                        ),
                        next_state,
                    )
                )
                step_num[0] += 1
                if beta <= alpha:
                    pruned_count[0] += len(actions) - index - 1
                    steps.append((step_num[0], "Cắt nhánh Alpha-Beta ở MAX vì beta <= alpha", state))
                    step_num[0] += 1
                    break
            return best_value, best_action

        best_value = float("inf")
        best_action = None
        for index, action in enumerate(actions):
            generated_count[0] += 1
            next_state = apply_min_action(state, action)
            value, _ = alphabeta(next_state, depth - 1, alpha, beta, True)
            old_beta = beta
            if value < best_value:
                best_value = value
                best_action = action
            beta = min(beta, best_value)
            steps.append(
                (
                    step_num[0],
                    (
                        f"MIN xét {action_to_text(action)} -> value={value}, "
                        f"alpha={alpha}, beta {old_beta}->{beta}"
                    ),
                    next_state,
                )
            )
            step_num[0] += 1
            if beta <= alpha:
                pruned_count[0] += len(actions) - index - 1
                steps.append((step_num[0], "Cắt nhánh Alpha-Beta ở MIN vì beta <= alpha", state))
                step_num[0] += 1
                break
        return best_value, best_action

    def replay_goal(path):
        replay_state = start_state
        for action in path:
            if not rules.can_move(replay_state, *action):
                return False
            replay_state = safe_apply_action(replay_state, rules, action)
        return replay_state.is_goal()

    current_state = start_state
    simulation_path = []
    max_replay_path = []

    for move_index in range(1, max_moves + 1):
        if current_state.is_goal():
            reason = "goal_found"
            break

        value, max_action = alphabeta(current_state, max_depth, -float("inf"), float("inf"), True)
        if max_action is None:
            reason = "no_max_action"
            steps.append((step_num[0], "MAX không có action để đi", current_state))
            step_num[0] += 1
            break

        current_state = safe_apply_action(current_state, rules, max_action)
        simulation_path.append(max_action)
        max_replay_path.append(max_action)
        steps.append((step_num[0], f"Simulation MAX chọn {action_to_text(max_action)} với value={value}", current_state))
        step_num[0] += 1

        if current_state.is_goal():
            reason = "goal_found"
            break

        min_value, min_action = alphabeta(current_state, max_depth, -float("inf"), float("inf"), False)
        if min_action is None:
            steps.append((step_num[0], "MIN bỏ lượt vì không có action hợp lệ", current_state))
            step_num[0] += 1
            continue

        current_state = apply_min_action(current_state, min_action)
        simulation_path.append(min_action)
        steps.append((step_num[0], f"Simulation MIN chọn {action_to_text(min_action)} với value={min_value}", current_state))
        step_num[0] += 1

    simulated_goal = current_state.is_goal()
    replay_solved = replay_goal(max_replay_path) if simulated_goal else False
    result_path = max_replay_path if replay_solved else []
    solved = replay_solved
    if simulated_goal and not replay_solved:
        reason = "simulated_goal_not_replayable_in_deterministic_ui"

    return SearchResult(
        algorithm="Alpha-Beta",
        solved=solved,
        path=result_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "pruned_count": pruned_count[0],
            "max_depth": max_depth,
            "evaluation_name": evaluation_name,
            "move_ordering": move_ordering,
            "simulation_moves": len(simulation_path),
            "simulation_path": simulation_path,
            "simulated_goal": simulated_goal,
            "reason": reason,
        },
    )
