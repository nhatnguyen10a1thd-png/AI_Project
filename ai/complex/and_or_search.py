# ai/complex/and_or_search.py
import time

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import action_to_text, safe_apply_action


def and_or_solve(start_state, rules, max_depth=8, max_nodes=20000, max_seconds=3.0):
    """
    AND-OR graph search from AIMA, adapted to a nondeterministic demo mode.

    OR nodes are agent choices.  AND nodes represent all possible environment
    outcomes.  An action is accepted only when every outcome has a conditional
    plan to a goal.  Squirrels Go Nuts is deterministic by default, so this file
    uses a documented "Slippery Mode": an action may move once or, if still
    legal, slip one extra cell in the same direction.
    """
    FAILURE = None
    GOAL = {"type": "goal"}

    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    steps = [(0, "Khởi tạo AND-OR Search: OR=agent chọn, AND=môi trường trả outcomes", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]
    outcome_count = [0]
    reason = ["search_exhausted"]

    def get_outcomes(state, action):
        """Return nondeterministic Slippery Mode outcomes without mutating state."""
        outcomes = {}

        one_step = safe_apply_action(state, rules, action)
        outcomes[one_step.encode()] = one_step

        piece_id, direction = action
        if rules.can_move(one_step, piece_id, direction):
            two_steps = safe_apply_action(one_step, rules, action)
            outcomes[two_steps.encode()] = two_steps

        result = list(outcomes.values())
        outcome_count[0] += len(result)
        return result

    def or_search(state, path, depth):
        visited_count[0] += 1

        if limit.reached(visited_count[0] + generated_count[0]):
            reason[0] = limit.reason(visited_count[0] + generated_count[0]) or "resource_limit"
            steps.append((step_num[0], f"OR dừng vì {reason[0]}", state))
            step_num[0] += 1
            return FAILURE

        if state.is_goal():
            steps.append((step_num[0], f"OR gặp goal tại depth={depth}", state))
            step_num[0] += 1
            return GOAL

        if depth >= max_depth:
            reason[0] = "depth_limit"
            steps.append((step_num[0], f"OR cutoff vì depth={depth} đạt max_depth={max_depth}", state))
            step_num[0] += 1
            return FAILURE

        state_code = state.encode()
        if state_code in path:
            reason[0] = "cycle_in_path"
            steps.append((step_num[0], "OR bỏ nhánh vì state lặp trong path hiện tại", state))
            step_num[0] += 1
            return FAILURE

        path = path | {state_code}
        legal_actions = list(rules.legal_actions(state))
        steps.append(
            (
                step_num[0],
                f"OR mở rộng depth={depth}, legal_actions={len(legal_actions)}",
                state,
            )
        )
        step_num[0] += 1

        if not legal_actions:
            reason[0] = "no_legal_action"
            steps.append((step_num[0], "OR thất bại vì không có action hợp lệ", state))
            step_num[0] += 1
            return FAILURE

        for action in legal_actions:
            outcomes = get_outcomes(state, action)
            generated_count[0] += len(outcomes)
            steps.append(
                (
                    step_num[0],
                    f"OR thử {action_to_text(action)} -> sinh {len(outcomes)} outcome cho AND",
                    state,
                )
            )
            step_num[0] += 1

            for index, outcome_state in enumerate(outcomes, start=1):
                steps.append(
                    (
                        step_num[0],
                        f"AND outcome {index}/{len(outcomes)} của {action_to_text(action)}",
                        outcome_state,
                    )
                )
                step_num[0] += 1

            subplan = and_search(outcomes, path, depth + 1, action)
            if subplan is not FAILURE:
                steps.append(
                    (
                        step_num[0],
                        f"OR chọn {action_to_text(action)} vì mọi outcome đều có plan",
                        state,
                    )
                )
                step_num[0] += 1
                return {"type": "action", "action": action, "branches": subplan}

            steps.append(
                (
                    step_num[0],
                    f"OR loại {action_to_text(action)} vì ít nhất một outcome thất bại",
                    state,
                )
            )
            step_num[0] += 1

        return FAILURE

    def and_search(states, path, depth, action):
        branches = {}
        steps.append(
            (
                step_num[0],
                f"AND kiểm tra {len(states)} outcome của {action_to_text(action)}",
                states[0] if states else start_state,
            )
        )
        step_num[0] += 1

        for index, outcome_state in enumerate(states, start=1):
            steps.append(
                (
                    step_num[0],
                    f"AND gọi OR cho outcome {index}/{len(states)}",
                    outcome_state,
                )
            )
            step_num[0] += 1

            subplan = or_search(outcome_state, path, depth)
            if subplan is FAILURE:
                steps.append(
                    (
                        step_num[0],
                        f"AND thất bại tại outcome {index}/{len(states)} -> action bị loại",
                        outcome_state,
                    )
                )
                step_num[0] += 1
                return FAILURE

            branches[outcome_state.encode()] = subplan

        steps.append((step_num[0], f"AND thành công: cả {len(states)} outcome đều có plan", states[0]))
        step_num[0] += 1
        return branches

    result_plan = or_search(start_state, path=set(), depth=0)
    solved = result_plan is not FAILURE
    if solved:
        reason[0] = "goal_plan_found"

    sample_path = []
    if solved and isinstance(result_plan, dict):
        current_plan = result_plan
        current_state = start_state
        while isinstance(current_plan, dict) and current_plan.get("type") == "action":
            action = current_plan["action"]
            sample_path.append(action)
            outcomes = get_outcomes(current_state, action)
            if not outcomes:
                break
            current_state = outcomes[0]
            current_plan = current_plan["branches"].get(current_state.encode())

    return SearchResult(
        algorithm="AND-OR Search",
        solved=solved,
        path=sample_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "plan_tree": str(result_plan),
            "sample_path_note": "Sample path chọn outcome đầu tiên để UI demo tuyến tính.",
            "nondeterministic_model": "Slippery Mode giả lập: action đi 1 ô hoặc trượt thêm 1 ô nếu còn hợp lệ.",
            "outcome_count": outcome_count[0],
            "reason": reason[0],
        },
    )
