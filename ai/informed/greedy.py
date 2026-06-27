# ai/informed/greedy.py
import heapq
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def greedy_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """
    Greedy Best-First Search from AIMA, adapted to Squirrels Go Nuts.

    The priority queue is ordered only by h(n), where h is the sum of nut-to-hole
    Manhattan distances.  Greedy search is often fast but is neither complete
    nor optimal under finite resource limits because it ignores g(n).
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    h_start = squirrel_heuristic(start_state)
    start_node = SearchNode(start_state)

    steps = [(0, f"Khởi tạo Greedy Best-First: h_start={h_start}", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reason = "frontier_empty"
    last_h = h_start

    extra_base = {
        "heuristic_name": HEURISTIC_NAME,
        "optimality_note": "Greedy chỉ xét h(n), không xét g(n), nên không đảm bảo tối ưu.",
    }

    if start_state.is_goal():
        return SearchResult(
            algorithm="Greedy",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={**extra_base, "last_h": h_start, "reason": "goal_at_start"},
        )

    frontier = []
    node_counter = 0
    heapq.heappush(frontier, (h_start, node_counter, start_node))
    frontier_encoded = {start_state.encode()}
    explored = set()

    while frontier:
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng Greedy vì {reason}", frontier[0][2].state))
            step_num += 1
            break

        h_val, _, node = heapq.heappop(frontier)
        last_h = h_val
        node_code = node.state.encode()
        frontier_encoded.discard(node_code)

        if node_code in explored:
            steps.append((step_num, f"Skip node h={h_val} vì đã explored", node.state))
            step_num += 1
            continue

        explored.add(node_code)
        visited_count += 1
        steps.append(
            (
                step_num,
                f"Pop node có h nhỏ nhất: depth={node.depth}, h={h_val}, frontier còn={len(frontier)}",
                node.state,
            )
        )
        step_num += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            steps.append((step_num, f"Tìm goal bằng Greedy, số bước={len(actions)}", node.state))
            return SearchResult(
                algorithm="Greedy",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={**extra_base, "last_h": h_val, "final_frontier_size": len(frontier), "reason": "goal_found"},
            )

        legal_actions = list(rules.legal_actions(node.state))
        steps.append((step_num, f"Mở rộng Greedy: legal_actions={len(legal_actions)}", node.state))
        step_num += 1

        for action in legal_actions:
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count += 1
            h_child = squirrel_heuristic(next_state)

            if next_code in explored:
                steps.append((step_num, f"Skip {action_to_text(action)} vì đã explored (h={h_child})", next_state))
                step_num += 1
                continue
            if next_code in frontier_encoded:
                steps.append((step_num, f"Skip {action_to_text(action)} vì đã có trong frontier (h={h_child})", next_state))
                step_num += 1
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1,
            )
            node_counter += 1
            heapq.heappush(frontier, (h_child, node_counter, child))
            frontier_encoded.add(next_code)
            steps.append(
                (
                    step_num,
                    f"Thử {action_to_text(action)} -> h={h_child}; đưa vào priority queue theo h",
                    next_state,
                )
            )
            step_num += 1

    return SearchResult(
        algorithm="Greedy",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={**extra_base, "last_h": last_h, "final_frontier_size": len(frontier), "reason": reason},
    )
