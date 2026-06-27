# ai/uninformed/bfs.py
import time
from collections import deque

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def bfs_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """
    Breadth-First Search as in AIMA, adapted to Squirrels Go Nuts.

    State is a GameState, action is a legal slide, goal test is
    GameState.is_goal(), and every action has unit cost.  With finite resource
    limits and unit action cost, BFS returns the shallowest solution it reaches
    before max_nodes/max_seconds.
    """
    start_time = time.time()
    start_node = SearchNode(start_state)
    start_code = start_state.encode()
    limit = SearchLimit(max_nodes, max_seconds)

    steps = [(0, "Khởi tạo BFS: FIFO queue, action cost = 1", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1

    extra_base = {
        "depth": 0,
        "final_frontier_size": 0,
        "unit_cost": True,
        "optimality_note": "BFS tìm lời giải nông nhất trong giới hạn tài nguyên vì mọi action có cost = 1.",
    }

    if start_state.is_goal():
        return SearchResult(
            algorithm="BFS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={**extra_base, "reason": "goal_at_start"},
        )

    frontier = deque([start_node])
    explored = set()
    frontier_encoded = {start_code}

    reason = "frontier_empty"
    while frontier:
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng BFS vì {reason}", frontier[0].state))
            step_num += 1
            break

        before_size = len(frontier)
        node = frontier.popleft()
        node_code = node.state.encode()
        frontier_encoded.discard(node_code)

        if node_code in explored:
            steps.append((step_num, f"Bỏ qua node depth={node.depth} vì đã explored", node.state))
            step_num += 1
            continue

        explored.add(node_code)
        visited_count += 1
        legal_actions = list(rules.legal_actions(node.state))
        steps.append(
            (
                step_num,
                (
                    f"Mở rộng node depth={node.depth}, g={node.path_cost}, "
                    f"frontier trước={before_size}, sau pop={len(frontier)}, "
                    f"legal_actions={len(legal_actions)}"
                ),
                node.state,
            )
        )
        step_num += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            steps.append((step_num, f"Tìm goal khi pop node, độ sâu lời giải={len(actions)}", node.state))
            return SearchResult(
                algorithm="BFS",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={**extra_base, "depth": len(actions), "final_frontier_size": len(frontier), "reason": "goal_found"},
            )

        for action in legal_actions:
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count += 1
            child_depth = node.depth + 1
            child_g = node.path_cost + 1

            if next_code in explored:
                steps.append((step_num, f"Skip {action_to_text(action)} vì state đã explored", next_state))
                step_num += 1
                continue
            if next_code in frontier_encoded:
                steps.append((step_num, f"Skip {action_to_text(action)} vì state đã nằm trong frontier", next_state))
                step_num += 1
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=child_g,
                depth=child_depth,
            )
            steps.append(
                (
                    step_num,
                    (
                        f"Thử {action_to_text(action)} -> enqueue depth={child_depth}, "
                        f"g={child_g}, frontier sau={len(frontier) + 1}"
                    ),
                    next_state,
                )
            )
            step_num += 1

            if next_state.is_goal():
                actions, _ = reconstruct_path(child)
                steps.append((step_num, f"Tìm goal khi sinh child, độ sâu lời giải={len(actions)}", next_state))
                return SearchResult(
                    algorithm="BFS",
                    solved=True,
                    path=actions,
                    visited_count=visited_count,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps,
                    extra={
                        **extra_base,
                        "depth": len(actions),
                        "final_frontier_size": len(frontier),
                        "reason": "goal_found",
                    },
                )

            frontier.append(child)
            frontier_encoded.add(next_code)

    return SearchResult(
        algorithm="BFS",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={**extra_base, "depth": None, "final_frontier_size": len(frontier), "reason": reason},
    )
