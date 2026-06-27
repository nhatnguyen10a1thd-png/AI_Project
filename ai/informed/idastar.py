# ai/informed/idastar.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def idastar_solve(
    start_state,
    rules,
    max_depth=60,
    max_threshold=120,
    max_nodes=20000,
    max_seconds=3.0,
):
    """
    Iterative Deepening A* from AIMA, adapted to Squirrels Go Nuts.

    The search performs DFS iterations bounded by threshold f=g+h.  It uses
    path-based cycle checking.  Like A*, optimality depends on the heuristic
    being admissible/consistent for the specific puzzle dynamics.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    h_start = squirrel_heuristic(start_state)
    threshold = h_start
    start_code = start_state.encode()

    steps = [(0, f"Khởi tạo IDA*: threshold ban đầu=h_start={h_start}", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    last_threshold = threshold
    reason = "threshold_limit"

    if start_state.is_goal():
        return SearchResult(
            algorithm="IDA*",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count[0],
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num[0], "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "heuristic_name": HEURISTIC_NAME,
                "last_threshold": threshold,
                "max_threshold": max_threshold,
                "reason": "goal_at_start",
            },
        )

    def search(node, current_threshold, path_encoded):
        visited_count[0] += 1
        h_val = squirrel_heuristic(node.state)
        f_val = node.path_cost + h_val

        if f_val > current_threshold:
            steps.append(
                (
                    step_num[0],
                    f"Cắt IDA*: f={f_val} > threshold={current_threshold} tại depth={node.depth}",
                    node.state,
                )
            )
            step_num[0] += 1
            return f_val, None, "cutoff"

        if node.state.is_goal():
            return f_val, node, "goal_found"

        if node.depth >= max_depth:
            steps.append((step_num[0], f"Cắt IDA*: đạt max_depth={max_depth}", node.state))
            step_num[0] += 1
            return float("inf"), None, "depth_limit"

        if limit.reached(generated_count[0]):
            return float("inf"), None, limit.reason(generated_count[0]) or "resource_limit"

        successors = []
        for action in rules.legal_actions(node.state):
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count[0] += 1

            if next_code in path_encoded:
                steps.append((step_num[0], f"IDA* skip {action_to_text(action)} vì lặp trong path", next_state))
                step_num[0] += 1
                continue

            h_child = squirrel_heuristic(next_state)
            child_f = node.path_cost + 1 + h_child
            successors.append((child_f, h_child, action, next_state, next_code))

        successors.sort(key=lambda item: (item[0], item[1], action_to_text(item[2])))
        min_next_threshold = float("inf")
        local_reason = "exhausted"

        for child_f, h_child, action, next_state, next_code in successors:
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1,
            )
            steps.append(
                (
                    step_num[0],
                    (
                        f"IDA* thử {action_to_text(action)}: g={child.path_cost}, "
                        f"h={h_child}, f={child_f}, threshold={current_threshold}"
                    ),
                    next_state,
                )
            )
            step_num[0] += 1

            path_encoded.add(next_code)
            overrun, result, child_reason = search(child, current_threshold, path_encoded)
            path_encoded.remove(next_code)

            if result is not None:
                return overrun, result, child_reason
            min_next_threshold = min(min_next_threshold, overrun)
            local_reason = child_reason

        return min_next_threshold, None, local_reason

    root = SearchNode(start_state)

    while threshold <= max_threshold and not limit.reached(generated_count[0]):
        last_threshold = threshold
        steps.append((step_num[0], f"=== IDA* iteration threshold={threshold} ===", start_state))
        step_num[0] += 1

        next_threshold, result_node, iter_reason = search(root, threshold, {start_code})
        if result_node is not None:
            actions, _ = reconstruct_path(result_node)
            steps.append((step_num[0], f"Tìm lời giải IDA*: cost={len(actions)}", result_node.state))
            return SearchResult(
                algorithm="IDA*",
                solved=True,
                path=actions,
                visited_count=visited_count[0],
                generated_count=generated_count[0],
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    "heuristic_name": HEURISTIC_NAME,
                    "last_threshold": threshold,
                    "max_threshold": max_threshold,
                    "reason": "goal_found",
                },
            )

        if next_threshold == float("inf"):
            reason = iter_reason
            steps.append((step_num[0], f"IDA* không còn threshold kế tiếp hữu hạn, reason={reason}", start_state))
            step_num[0] += 1
            break

        steps.append((step_num[0], f"IDA* nâng threshold: {threshold} -> {next_threshold}", start_state))
        step_num[0] += 1
        threshold = next_threshold

    if limit.reached(generated_count[0]):
        reason = limit.reason(generated_count[0]) or "resource_limit"
    elif threshold > max_threshold:
        reason = "max_threshold"

    return SearchResult(
        algorithm="IDA*",
        solved=False,
        path=[],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "last_threshold": last_threshold,
            "max_threshold": max_threshold,
            "reason": reason,
        },
    )
