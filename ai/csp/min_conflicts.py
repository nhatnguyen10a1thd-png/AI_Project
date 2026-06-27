# ai/csp/min_conflicts.py
import random
import time

from ai.search_result import SearchResult
from ai.utils import action_to_text, safe_apply_action


def min_conflicts_solve(start_state, rules, k=15, max_steps=100, seed=None):
    """
    Min-Conflicts local search adapted to action-plan CSPs.

    Variables A_0..A_{k-1} are planned actions.  The domain is every direction
    for every movable piece in the start state.  Conflicts include illegal
    actions at execution time, repeated states/cycles, and active nuts remaining
    after k actions.  At each step the algorithm chooses a variable from the
    conflicted variables, then assigns a domain value with the lowest conflict
    score.
    """
    start_time = time.time()
    rng = random.Random(seed)

    movable_ids = [pid for pid, piece in start_state.pieces.items() if piece.movable]
    domain = [(pid, direction) for pid in movable_ids for direction in ("UP", "DOWN", "LEFT", "RIGHT")]
    steps = [(0, f"Khởi tạo Min-Conflicts: k={k}, domain_size={len(domain)}", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 0

    if start_state.is_goal():
        return SearchResult(
            algorithm="Min-Conflicts",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=0,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "final_conflict_score": 0,
                "k": k,
                "max_steps": max_steps,
                "conflict_breakdown": {},
                "reason": "goal_at_start",
            },
        )

    if not domain:
        return SearchResult(
            algorithm="Min-Conflicts",
            solved=False,
            path=[],
            visited_count=0,
            generated_count=0,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Domain rỗng: không có movable piece", start_state)],
            extra={
                "final_conflict_score": None,
                "k": k,
                "max_steps": max_steps,
                "conflict_breakdown": {"empty_domain": True},
                "reason": "empty_domain",
            },
        )

    def evaluate_path(path):
        current_state = start_state
        states_path = [current_state]
        visited_states = {current_state.encode(): 0}
        illegal_indices = []
        cycle_indices = []
        goal_reached_at = -1

        for index, action in enumerate(path):
            if goal_reached_at != -1:
                states_path.append(current_state)
                continue

            if not rules.can_move(current_state, *action):
                illegal_indices.append(index)
                states_path.append(current_state)
                continue

            current_state = safe_apply_action(current_state, rules, action)
            current_code = current_state.encode()
            if current_code in visited_states:
                cycle_indices.append(index)
            visited_states[current_code] = index + 1
            states_path.append(current_state)

            if current_state.is_goal():
                goal_reached_at = index

        remaining_nuts = sum(
            1 for piece in current_state.pieces.values()
            if piece.type == "squirrel" and piece.has_nut
        )
        goal_missing = 0 if goal_reached_at != -1 else remaining_nuts

        conflicted_indices = set(illegal_indices) | set(cycle_indices)
        if goal_reached_at == -1:
            conflicted_indices.update(range(len(path)))

        conflict_breakdown = {
            "illegal_actions": len(illegal_indices),
            "cycle_hits": len(cycle_indices),
            "remaining_nuts": remaining_nuts,
            "goal_missing": goal_missing,
            "illegal_indices": illegal_indices,
            "cycle_indices": cycle_indices,
        }
        conflict_score = (
            conflict_breakdown["illegal_actions"] * 10
            + conflict_breakdown["cycle_hits"] * 5
            + conflict_breakdown["goal_missing"] * 20
        )
        return (
            conflict_score,
            states_path,
            goal_reached_at,
            sorted(conflicted_indices),
            conflict_breakdown,
        )

    path = [rng.choice(domain) for _ in range(k)]
    best_path = list(path)
    best_score, best_states, best_goal, _, best_breakdown = evaluate_path(best_path)

    for step in range(max_steps):
        conflict_score, states_path, goal_reached_at, conflicted_indices, breakdown = evaluate_path(path)
        visited_count += 1

        if conflict_score < best_score or (best_goal == -1 and goal_reached_at != -1):
            best_path = list(path)
            best_score = conflict_score
            best_states = states_path
            best_goal = goal_reached_at
            best_breakdown = breakdown

        display_state = states_path[min(len(states_path) - 1, goal_reached_at + 1)] if goal_reached_at != -1 else states_path[-1]
        steps.append(
            (
                step_num,
                f"Step {step}: conflict_score={conflict_score}, conflicted_indices={conflicted_indices}",
                display_state,
            )
        )
        step_num += 1

        if goal_reached_at != -1:
            actual_path = path[:goal_reached_at + 1]
            actual_states = states_path[:goal_reached_at + 2]
            for index, action in enumerate(actual_path, start=1):
                steps.append((step_num, f"Solution step {index}: {action_to_text(action)}", actual_states[index]))
                step_num += 1
            return SearchResult(
                algorithm="Min-Conflicts",
                solved=True,
                path=actual_path,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    "final_conflict_score": conflict_score,
                    "k": k,
                    "max_steps": max_steps,
                    "conflict_breakdown": breakdown,
                    "reason": "goal_found",
                },
            )

        if not conflicted_indices:
            conflicted_indices = list(range(k))

        var_index = rng.choice(conflicted_indices)
        steps.append((step_num, f"Chọn biến xung đột A_{var_index}", states_path[min(var_index, len(states_path) - 1)]))
        step_num += 1

        original_value = path[var_index]
        scored_values = []
        for value in domain:
            candidate_path = list(path)
            candidate_path[var_index] = value
            score, candidate_states, candidate_goal, _, candidate_breakdown = evaluate_path(candidate_path)
            generated_count += 1
            scored_values.append((score, action_to_text(value), value, candidate_states, candidate_goal, candidate_breakdown))
            steps.append(
                (
                    step_num,
                    f"Thử A_{var_index}={action_to_text(value)} -> conflict_score={score}",
                    candidate_states[min(len(candidate_states) - 1, var_index + 1)],
                )
            )
            step_num += 1

        best_value_score = min(item[0] for item in scored_values)
        best_values = [item for item in scored_values if item[0] == best_value_score]
        _, _, chosen_value, _, _, _ = rng.choice(best_values)
        path[var_index] = chosen_value
        steps.append(
            (
                step_num,
                (
                    f"Gán A_{var_index}={action_to_text(chosen_value)} vì score thấp nhất={best_value_score} "
                    f"(trước đó {action_to_text(original_value)})"
                ),
                states_path[min(var_index, len(states_path) - 1)],
            )
        )
        step_num += 1

    if best_goal != -1:
        reason = "best_path_reaches_goal_but_not_current"
    else:
        reason = "max_steps"

    steps.append(
        (
            step_num,
            f"Không tìm được goal trong max_steps; best_conflict_score={best_score}, best_path_prefix={best_path}",
            best_states[-1],
        )
    )

    return SearchResult(
        algorithm="Min-Conflicts",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "final_conflict_score": best_score,
            "k": k,
            "max_steps": max_steps,
            "conflict_breakdown": best_breakdown,
            "best_path": best_path,
            "reason": reason,
        },
    )
