# ai/informed/astar.py
import heapq
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def astar_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """
    A* Search from AIMA, adapted to Squirrels Go Nuts.

    State is a GameState, action is a legal slide, step cost is 1, and the
    priority is f(n)=g(n)+h(n).  This implementation keeps g_score and reopens
    a state when a strictly better path is found.  Optimality still depends on
    h being admissible/consistent for the puzzle instance.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    h_start = squirrel_heuristic(start_state)
    f_start = h_start
    start_node = SearchNode(start_state)
    start_code = start_state.encode()

    steps = [(0, f"Khởi tạo A*: g=0, h={h_start}, f={f_start}", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reopened_count = 0
    last_f = f_start
    reason = "frontier_empty"

    extra_base = {
        "heuristic_name": HEURISTIC_NAME,
        "optimality_note": (
            "A* tối ưu khi heuristic admissible/consistent; implementation này hỗ trợ reopen "
            "khi tìm được g tốt hơn."
        ),
    }

    if start_state.is_goal():
        return SearchResult(
            algorithm="A*",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={**extra_base, "last_f": f_start, "reopened_count": 0, "reason": "goal_at_start"},
        )

    frontier = []
    node_counter = 0
    heapq.heappush(frontier, (f_start, node_counter, start_node))
    g_score = {start_code: 0}
    closed_g = {}

    while frontier:
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng A* vì {reason}", frontier[0][2].state))
            step_num += 1
            break

        f_val, _, node = heapq.heappop(frontier)
        last_f = f_val
        node_code = node.state.encode()
        best_known_g = g_score.get(node_code, float("inf"))

        if node.path_cost > best_known_g:
            steps.append(
                (
                    step_num,
                    f"Skip stale node: g={node.path_cost} > best_g={best_known_g}, f={f_val}",
                    node.state,
                )
            )
            step_num += 1
            continue

        if node_code in closed_g and node.path_cost >= closed_g[node_code]:
            steps.append((step_num, f"Skip duplicate closed node với g={node.path_cost}, f={f_val}", node.state))
            step_num += 1
            continue

        closed_g[node_code] = node.path_cost
        visited_count += 1
        h_val = squirrel_heuristic(node.state)
        steps.append(
            (
                step_num,
                f"Pop node có f nhỏ nhất: depth={node.depth}, g={node.path_cost}, h={h_val}, f={f_val}",
                node.state,
            )
        )
        step_num += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            steps.append((step_num, f"Tìm goal khi pop node, solution_cost={len(actions)}", node.state))
            return SearchResult(
                algorithm="A*",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    **extra_base,
                    "last_f": f_val,
                    "reopened_count": reopened_count,
                    "final_frontier_size": len(frontier),
                    "reason": "goal_found",
                },
            )

        legal_actions = list(rules.legal_actions(node.state))
        steps.append((step_num, f"Mở rộng A*: legal_actions={len(legal_actions)}", node.state))
        step_num += 1

        for action in legal_actions:
            next_state = safe_apply_action(node.state, rules, action)
            next_code = next_state.encode()
            generated_count += 1
            g_new = node.path_cost + 1

            old_g = g_score.get(next_code, float("inf"))
            if g_new >= old_g:
                steps.append(
                    (
                        step_num,
                        f"Skip {action_to_text(action)} vì g_new={g_new} không tốt hơn best_g={old_g}",
                        next_state,
                    )
                )
                step_num += 1
                continue

            if next_code in closed_g:
                reopened_count += 1
                steps.append(
                    (
                        step_num,
                        f"Reopen state qua {action_to_text(action)} vì g_new={g_new} < closed_g={closed_g[next_code]}",
                        next_state,
                    )
                )
                step_num += 1
                del closed_g[next_code]

            h_new = squirrel_heuristic(next_state)
            f_new = g_new + h_new
            g_score[next_code] = g_new
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=g_new,
                depth=node.depth + 1,
            )
            node_counter += 1
            heapq.heappush(frontier, (f_new, node_counter, child))
            steps.append(
                (
                    step_num,
                    f"Thử {action_to_text(action)} -> g={g_new}, h={h_new}, f={f_new}; push frontier",
                    next_state,
                )
            )
            step_num += 1

    return SearchResult(
        algorithm="A*",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            **extra_base,
            "last_f": last_f,
            "reopened_count": reopened_count,
            "final_frontier_size": len(frontier),
            "reason": reason,
        },
    )
