# ai/csp/backtracking.py
import time

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import action_to_text, safe_apply_action


def backtracking_solve(start_state, rules, max_depth=15, max_nodes=20000, max_seconds=3.0):
    """
    CSP-style Backtracking over action variables A_0..A_{d-1}.

    Variable A_i is the action chosen at depth i.  Its domain is the legal
    actions in the current forwarded state.  Constraints require the action to
    be legal, the next state to be the result of the previous state, and some
    state in the path to satisfy GameState.is_goal().  Path-based cycle checking
    avoids loops in the current assignment without pruning other branches.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    steps = [(0, f"Khởi tạo CSP-style Backtracking: biến A_0..A_{max_depth - 1}", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    reason = ["depth_limit"]

    if start_state.is_goal():
        return SearchResult(
            algorithm="Backtracking",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count[0],
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num[0], "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "max_depth": max_depth,
                "variables_model": "A_i là action ở bước i; domain là legal actions theo state hiện tại.",
                "reason": "goal_at_start",
            },
        )

    def backtrack(state, path, path_encoded):
        visited_count[0] += 1

        if limit.reached(generated_count[0]):
            reason[0] = limit.reason(generated_count[0]) or "resource_limit"
            steps.append((step_num[0], f"Dừng Backtracking vì {reason[0]}", state))
            step_num[0] += 1
            return None

        if state.is_goal():
            reason[0] = "goal_found"
            steps.append((step_num[0], f"Goal constraint thỏa tại depth={len(path)}", state))
            step_num[0] += 1
            return path

        if len(path) >= max_depth:
            reason[0] = "depth_limit"
            steps.append((step_num[0], f"Quay lui vì đạt max_depth={max_depth}", state))
            step_num[0] += 1
            return None

        variable_name = f"A_{len(path)}"
        legal_actions = list(rules.legal_actions(state))
        steps.append(
            (
                step_num[0],
                f"Chọn biến {variable_name}, domain_size={len(legal_actions)}",
                state,
            )
        )
        step_num[0] += 1

        if not legal_actions:
            reason[0] = "no_legal_action"
            steps.append((step_num[0], f"{variable_name} có domain rỗng", state))
            step_num[0] += 1
            return None

        for action in legal_actions:
            steps.append((step_num[0], f"Gán thử {variable_name}={action_to_text(action)}", state))
            step_num[0] += 1

            next_state = safe_apply_action(state, rules, action)
            next_code = next_state.encode()
            generated_count[0] += 1

            if next_code in path_encoded:
                steps.append(
                    (
                        step_num[0],
                        f"Ràng buộc cycle fail: {variable_name}={action_to_text(action)} đưa về state trong path",
                        next_state,
                    )
                )
                step_num[0] += 1
                continue

            steps.append(
                (
                    step_num[0],
                    f"Forward state sau {variable_name}={action_to_text(action)} hợp lệ",
                    next_state,
                )
            )
            step_num[0] += 1

            path_encoded.add(next_code)
            result = backtrack(next_state, path + [action], path_encoded)
            path_encoded.remove(next_code)

            if result is not None:
                return result

            steps.append((step_num[0], f"Quay lui khỏi {variable_name}={action_to_text(action)}", state))
            step_num[0] += 1

        return None

    solution_path = backtrack(start_state, [], {start_state.encode()})
    solved = solution_path is not None

    return SearchResult(
        algorithm="Backtracking",
        solved=solved,
        path=solution_path or [],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "max_depth": max_depth,
            "variables_model": "A_i là action ở bước i; constraints gồm legality, transition consistency, path acyclic, goal.",
            "reason": "goal_found" if solved else reason[0],
        },
    )
