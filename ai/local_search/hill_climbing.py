# ai/local_search/hill_climbing.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def hill_climbing_solve(start_state, rules, max_iterations=200, max_nodes=20000, max_seconds=3.0):
    """
    Simple Hill Climbing adapted from AIMA local search.

    State is a GameState, neighbor states are legal slides, and value(state) is
    -h(state), so higher is better.  The algorithm accepts the first strictly
    better neighbor and stops at a local optimum, a goal, or a safety limit.
    It is not complete and not optimal.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    current_node = SearchNode(start_state)
    current_h = squirrel_heuristic(start_state)
    current_value = -current_h

    steps = [(0, f"Khởi tạo Simple Hill Climbing: h={current_h}, value={current_value}", start_state)]
    step_num = 1
    visited_count = 1
    generated_count = 1
    reason = "local_optimum"

    if start_state.is_goal():
        return SearchResult(
            algorithm="Hill Climbing",
            solved=True,
            path=[],
            visited_count=visited_count,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={"final_value": current_value, "final_h": current_h, "reason": "goal_at_start"},
        )

    for iteration in range(1, max_iterations + 1):
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng Hill Climbing vì {reason}", current_node.state))
            step_num += 1
            break

        legal_actions = list(rules.legal_actions(current_node.state))
        steps.append(
            (
                step_num,
                f"Iteration {iteration}: current_h={current_h}, current_value={current_value}, neighbors={len(legal_actions)}",
                current_node.state,
            )
        )
        step_num += 1

        if not legal_actions:
            reason = "no_legal_action"
            steps.append((step_num, "Dừng vì không có action hợp lệ", current_node.state))
            step_num += 1
            break

        found_better = False
        for action in legal_actions:
            next_state = safe_apply_action(current_node.state, rules, action)
            next_h = squirrel_heuristic(next_state)
            next_value = -next_h
            generated_count += 1
            steps.append(
                (
                    step_num,
                    f"Xét neighbor {action_to_text(action)}: h={next_h}, value={next_value}",
                    next_state,
                )
            )
            step_num += 1

            if next_value > current_value:
                current_node = SearchNode(
                    state=next_state,
                    parent=current_node,
                    action=action,
                    path_cost=current_node.path_cost + 1,
                    depth=current_node.depth + 1,
                )
                current_h = next_h
                current_value = next_value
                visited_count += 1
                found_better = True
                steps.append(
                    (
                        step_num,
                        f"Chọn {action_to_text(action)} vì value tăng lên {current_value}",
                        next_state,
                    )
                )
                step_num += 1
                break

        if current_node.state.is_goal():
            reason = "goal_found"
            steps.append((step_num, f"Goal đạt được sau {current_node.depth} bước", current_node.state))
            step_num += 1
            break

        if not found_better:
            reason = "local_optimum"
            steps.append(
                (
                    step_num,
                    f"Dừng vì local optimum: không có neighbor nào tốt hơn value={current_value}",
                    current_node.state,
                )
            )
            step_num += 1
            break
    else:
        reason = "max_iterations"

    solved = current_node.state.is_goal()
    actions, _ = reconstruct_path(current_node) if solved else ([], [])
    return SearchResult(
        algorithm="Hill Climbing",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "final_value": current_value,
            "final_h": current_h,
            "reason": reason,
            "optimality_note": "Simple Hill Climbing không complete và không tối ưu.",
        },
    )
