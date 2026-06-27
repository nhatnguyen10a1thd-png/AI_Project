# ai/complex/online_search.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def online_search_solve(start_state, rules, max_steps=200, max_nodes=20000, max_seconds=3.0):
    """
    LRTA*-style online search from AIMA, adapted to Squirrels Go Nuts.

    The agent observes only legal successors of the current state, updates
    learned_h[current] = min(1 + learned_h[next]), and moves to the successor
    with the smallest estimated cost.  A revisit cutoff is used only as a demo
    safety guard against loops.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    steps = [(0, "Khởi tạo Online Search / LRTA*: quan sát successor của current state", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reason = "max_steps"
    safety_cutoff = 8

    if start_state.is_goal():
        return SearchResult(
            algorithm="Online Search",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "learned_states": 1,
                "revisit_count": 0,
                "safety_cutoff": safety_cutoff,
                "reason": "goal_at_start",
            },
        )

    learned_h = {start_state.encode(): squirrel_heuristic(start_state)}
    revisit_count = {start_state.encode(): 1}
    total_revisits = 0
    current_node = SearchNode(start_state)

    for step in range(1, max_steps + 1):
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng LRTA* vì {reason}", current_node.state))
            step_num += 1
            break
        if current_node.state.is_goal():
            reason = "goal_found"
            break

        current_code = current_node.state.encode()
        old_h = learned_h.get(current_code, squirrel_heuristic(current_node.state))
        successors = []
        visited_count += 1

        legal_actions = list(rules.legal_actions(current_node.state))
        steps.append(
            (
                step_num,
                f"LRTA* step={step}: current_h={old_h}, quan sát {len(legal_actions)} successor",
                current_node.state,
            )
        )
        step_num += 1

        for action in legal_actions:
            next_state = safe_apply_action(current_node.state, rules, action)
            next_code = next_state.encode()
            if next_code not in learned_h:
                learned_h[next_code] = squirrel_heuristic(next_state)
            estimate = 1 + learned_h[next_code]
            successors.append((estimate, learned_h[next_code], action, next_state, next_code))
            generated_count += 1
            steps.append(
                (
                    step_num,
                    f"Successor {action_to_text(action)}: learned_h[next]={learned_h[next_code]}, cost+h={estimate}",
                    next_state,
                )
            )
            step_num += 1

        if not successors:
            reason = "no_legal_action"
            steps.append((step_num, "Dừng LRTA* vì không có successor hợp lệ", current_node.state))
            step_num += 1
            break

        successors.sort(key=lambda item: (item[0], item[1], action_to_text(item[2])))
        best_estimate, h_next, action, next_state, next_code = successors[0]
        learned_h[current_code] = best_estimate
        steps.append(
            (
                step_num,
                (
                    f"Cập nhật learned_h[current]: {old_h} -> {best_estimate}; "
                    f"chọn {action_to_text(action)} vì estimated cost nhỏ nhất"
                ),
                current_node.state,
            )
        )
        step_num += 1

        current_node = SearchNode(
            state=next_state,
            parent=current_node,
            action=action,
            path_cost=current_node.path_cost + 1,
            depth=current_node.depth + 1,
        )
        revisit_count[next_code] = revisit_count.get(next_code, 0) + 1
        if revisit_count[next_code] > 1:
            total_revisits += 1

        steps.append(
            (
                step_num,
                f"Đi sang {action_to_text(action)}: h_next={h_next}, revisit_state={revisit_count[next_code]}",
                next_state,
            )
        )
        step_num += 1

        if revisit_count[next_code] > safety_cutoff and not next_state.is_goal():
            reason = "safety_revisit_cutoff"
            steps.append(
                (
                    step_num,
                    f"Dừng do safety cutoff: state bị revisit {revisit_count[next_code]} lần",
                    next_state,
                )
            )
            step_num += 1
            break

    solved = current_node.state.is_goal()
    if solved:
        reason = "goal_found"
    actions, _ = reconstruct_path(current_node) if solved else ([], [])

    return SearchResult(
        algorithm="Online Search",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "learned_states": len(learned_h),
            "revisit_count": total_revisits,
            "safety_cutoff": safety_cutoff,
            "reason": reason,
        },
    )
