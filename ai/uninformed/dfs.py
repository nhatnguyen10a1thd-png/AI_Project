# ai/uninformed/dfs.py
import time

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def dfs_solve(start_state, rules, max_depth=40, max_nodes=20000, max_seconds=3.0):
    """
    Depth-limited graph DFS adapted from the AIMA depth-first idea.

    State is a GameState, action is a legal slide, goal test is
    GameState.is_goal(), and the search uses path-based cycle checking rather
    than a global explored set so alternative paths are not pruned too
    aggressively.  DFS is not optimal and is complete only within max_depth and
    the resource limits.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    start_node = SearchNode(start_state)
    start_code = start_state.encode()

    steps = [(0, f"Khởi tạo Depth-limited Graph DFS: max_depth={max_depth}", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reason = "stack_empty"

    if start_state.is_goal():
        return SearchResult(
            algorithm="DFS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={"depth": 0, "final_frontier_size": 0, "max_depth": max_depth, "reason": "goal_at_start"},
        )

    stack = [(start_node, {start_code})]

    while stack:
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng DFS vì {reason}", stack[-1][0].state))
            step_num += 1
            break

        node, path_encoded = stack.pop()
        visited_count += 1
        steps.append(
            (
                step_num,
                f"Pop stack: depth={node.depth}, g={node.path_cost}, stack còn={len(stack)}",
                node.state,
            )
        )
        step_num += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            steps.append((step_num, f"Tìm goal ở depth={node.depth}, số bước={len(actions)}", node.state))
            return SearchResult(
                algorithm="DFS",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    "depth": len(actions),
                    "final_frontier_size": len(stack),
                    "max_depth": max_depth,
                    "reason": "goal_found",
                    "optimality_note": "DFS không đảm bảo lời giải tối ưu.",
                },
            )

        if node.depth >= max_depth:
            steps.append((step_num, f"Cutoff depth limit tại depth={node.depth}", node.state))
            step_num += 1
            reason = "depth_limit"
            continue

        legal_actions = list(rules.legal_actions(node.state))
        steps.append((step_num, f"Mở rộng DFS depth={node.depth}, legal_actions={len(legal_actions)}", node.state))
        step_num += 1

        for action in reversed(legal_actions):
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count += 1

            if next_code in path_encoded:
                steps.append(
                    (
                        step_num,
                        f"Skip {action_to_text(action)} vì state đã nằm trong path hiện tại",
                        next_state,
                    )
                )
                step_num += 1
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1,
            )
            child_path = set(path_encoded)
            child_path.add(next_code)
            stack.append((child, child_path))
            steps.append(
                (
                    step_num,
                    f"Push {action_to_text(action)} vào stack: depth={child.depth}, g={child.path_cost}",
                    next_state,
                )
            )
            step_num += 1

    return SearchResult(
        algorithm="DFS",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "depth": None,
            "final_frontier_size": len(stack),
            "max_depth": max_depth,
            "reason": reason,
            "optimality_note": "DFS là tìm kiếm theo chiều sâu, không đảm bảo tối ưu.",
        },
    )
