# ai/uninformed/ids.py
import time

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def ids_solve(start_state, rules, max_depth=25, max_nodes=20000, max_seconds=3.0):
    """
    Iterative Deepening Search from AIMA, adapted to Squirrels Go Nuts.

    The outer loop increases the depth limit.  Each inner depth-limited search
    uses path-based cycle checking and does not keep a global explored set
    across iterations.  With unit action cost, IDS finds the shallowest solution
    it reaches within max_depth and resource limits.
    """
    start_time = time.time()
    limit_guard = SearchLimit(max_nodes, max_seconds)
    steps = [(0, f"Khởi tạo IDS: tăng depth limit từ 0 đến {max_depth}", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    iterations = []
    reason = "depth_limit"

    if start_state.is_goal():
        return SearchResult(
            algorithm="IDS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count[0],
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num[0], "Goal ngay tại state khởi tạo", start_state)],
            extra={"depth": 0, "final_frontier_size": 0, "max_depth": max_depth, "reason": "goal_at_start"},
        )

    def dls(node, depth_limit, path_encoded, iteration_stats):
        visited_count[0] += 1
        iteration_stats["visited"] += 1

        if limit_guard.reached(generated_count[0]):
            return None, False, limit_guard.reason(generated_count[0]) or "resource_limit"

        if node.state.is_goal():
            return node, False, "goal_found"

        if node.depth >= depth_limit:
            steps.append((step_num[0], f"Cutoff IDS tại depth={node.depth}/{depth_limit}", node.state))
            step_num[0] += 1
            return None, True, "cutoff"

        legal_actions = list(rules.legal_actions(node.state))
        steps.append(
            (
                step_num[0],
                f"DLS mở rộng depth={node.depth}/{depth_limit}, legal_actions={len(legal_actions)}",
                node.state,
            )
        )
        step_num[0] += 1

        cutoff_occurred = False
        for action in legal_actions:
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count[0] += 1
            iteration_stats["generated"] += 1

            if next_code in path_encoded:
                steps.append(
                    (
                        step_num[0],
                        f"IDS skip {action_to_text(action)} vì state lặp trong path hiện tại",
                        next_state,
                    )
                )
                step_num[0] += 1
                continue

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
                    f"IDS thử A_{child.depth - 1}={action_to_text(action)}: depth={child.depth}/{depth_limit}",
                    next_state,
                )
            )
            step_num[0] += 1

            path_encoded.add(next_code)
            result, cutoff, child_reason = dls(child, depth_limit, path_encoded, iteration_stats)
            path_encoded.remove(next_code)

            if result is not None:
                return result, False, child_reason
            if cutoff:
                cutoff_occurred = True

        return None, cutoff_occurred, "cutoff" if cutoff_occurred else "exhausted"

    root = SearchNode(start_state)
    start_code = start_state.encode()

    for depth_limit in range(max_depth + 1):
        if limit_guard.reached(generated_count[0]):
            reason = limit_guard.reason(generated_count[0]) or "resource_limit"
            steps.append((step_num[0], f"Dừng IDS trước iteration mới vì {reason}", start_state))
            step_num[0] += 1
            break

        iteration_stats = {"limit": depth_limit, "visited": 0, "generated": 0}
        steps.append((step_num[0], f"=== IDS bắt đầu depth_limit={depth_limit} ===", start_state))
        step_num[0] += 1

        result_node, cutoff, iter_reason = dls(root, depth_limit, {start_code}, iteration_stats)
        iteration_stats["cutoff"] = cutoff
        iteration_stats["reason"] = iter_reason
        iterations.append(iteration_stats)

        steps.append(
            (
                step_num[0],
                (
                    f"IDS kết thúc depth_limit={depth_limit}: "
                    f"visited={iteration_stats['visited']}, generated={iteration_stats['generated']}, "
                    f"cutoff={cutoff}, reason={iter_reason}"
                ),
                start_state,
            )
        )
        step_num[0] += 1

        if result_node is not None:
            actions, _ = reconstruct_path(result_node)
            steps.append((step_num[0], f"Tìm thấy lời giải ở depth={len(actions)}", result_node.state))
            return SearchResult(
                algorithm="IDS",
                solved=True,
                path=actions,
                visited_count=visited_count[0],
                generated_count=generated_count[0],
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    "depth": len(actions),
                    "final_frontier_size": 0,
                    "max_depth": max_depth,
                    "iterations": iterations,
                    "reason": "goal_found",
                    "optimality_note": "IDS tìm lời giải nông nhất trong giới hạn depth/resource với action cost = 1.",
                },
            )

        if not cutoff:
            reason = iter_reason
            break

    return SearchResult(
        algorithm="IDS",
        solved=False,
        path=[],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "depth": None,
            "final_frontier_size": 0,
            "max_depth": max_depth,
            "iterations": iterations,
            "reason": reason,
        },
    )
