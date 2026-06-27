# ai/local_search/simulated_annealing.py
import math
import random
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def simulated_annealing_solve(
    start_state,
    rules,
    max_iterations=500,
    init_temp=10.0,
    cooling_rate=0.95,
    seed=None,
):
    """
    Simulated Annealing from AIMA, adapted to Squirrels Go Nuts.

    State is a GameState, neighbors are legal slides, and value(state)=-h(state).
    Better states are accepted immediately.  Worse states are accepted with
    P=exp(delta_E/T).  This stochastic local search is not complete and not
    guaranteed optimal.
    """
    start_time = time.time()
    rng = random.Random(seed)
    current_node = SearchNode(start_state)
    current_h = squirrel_heuristic(start_state)
    current_value = -current_h
    temp = init_temp

    steps = [(0, f"Khởi tạo Simulated Annealing: value={current_value}, h={current_h}, T={temp:.3f}", start_state)]
    step_num = 1
    visited_count = 1
    generated_count = 1
    reason = "max_iterations"

    if start_state.is_goal():
        return SearchResult(
            algorithm="Simulated Annealing",
            solved=True,
            path=[],
            visited_count=visited_count,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "final_temp": temp,
                "final_value": current_value,
                "final_h": current_h,
                "reason": "goal_at_start",
            },
        )

    for iteration in range(1, max_iterations + 1):
        if current_node.state.is_goal():
            reason = "goal_found"
            break
        if temp <= 0.0001:
            reason = "temperature_zero"
            steps.append((step_num, f"Dừng vì nhiệt độ quá thấp T={temp:.6f}", current_node.state))
            step_num += 1
            break

        legal_actions = list(rules.legal_actions(current_node.state))
        if not legal_actions:
            reason = "no_legal_action"
            steps.append((step_num, "Dừng vì không có action hợp lệ", current_node.state))
            step_num += 1
            break

        action = rng.choice(legal_actions)
        next_state = safe_apply_action(current_node.state, rules, action)
        next_h = squirrel_heuristic(next_state)
        next_value = -next_h
        generated_count += 1

        delta_e = next_value - current_value
        probability = 1.0 if delta_e > 0 else math.exp(delta_e / temp)
        sample = rng.random()
        accepted = delta_e > 0 or sample < probability

        steps.append(
            (
                step_num,
                (
                    f"Iter {iteration}: thử {action_to_text(action)}, T={temp:.3f}, "
                    f"current_value={current_value}, next_value={next_value}, "
                    f"delta_E={delta_e}, P={probability:.3f}, sample={sample:.3f}"
                ),
                next_state,
            )
        )
        step_num += 1

        if accepted:
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
            accept_reason = "tốt hơn" if delta_e > 0 else "chấp nhận xác suất"
            steps.append((step_num, f"Accept {action_to_text(action)} vì {accept_reason}", next_state))
            step_num += 1
        else:
            steps.append((step_num, f"Reject {action_to_text(action)} vì sample >= P", current_node.state))
            step_num += 1

        temp *= cooling_rate

    solved = current_node.state.is_goal()
    if solved:
        reason = "goal_found"
    actions, _ = reconstruct_path(current_node) if solved else ([], [])

    return SearchResult(
        algorithm="Simulated Annealing",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "final_temp": temp,
            "final_value": current_value,
            "final_h": current_h,
            "reason": reason,
            "seed": seed,
            "optimality_note": "Simulated Annealing là local stochastic search, không đảm bảo complete/tối ưu.",
        },
    )
