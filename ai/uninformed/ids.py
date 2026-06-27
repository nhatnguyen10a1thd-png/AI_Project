# ai/uninformed/ids.py
import time
from ai.utils import SearchNode, reconstruct_path
from ai.search_result import SearchResult
from ai.limits import SearchLimit


def ids_solve(start_state, rules, max_depth=25, max_nodes=20000, max_seconds=3.0):
    """
    Solves the puzzle using Iterative Deepening Search (IDS).
    Increases the depth limit from 0 to max_depth.
    Each iteration performs a Depth-Limited DFS.
    Guarantees finding the shallowest solution (like BFS) with O(d) memory.
    """
    start_time = time.time()

    if start_state.is_goal():
        return SearchResult(
            algorithm="IDS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, "Start (Goal reached immediately)", start_state)]
        )

    steps = [(0, "Start - IDS bắt đầu tìm kiếm tăng dần độ sâu", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    limit_guard = SearchLimit(max_nodes, max_seconds)

    # ------------------------------------------------------------------ #
    # Inner DLS (Depth-Limited Search) — recursive, path-based visited     #
    # ------------------------------------------------------------------ #
    def dls(node, limit, path_encoded):
        """
        Returns (solution_node or None, cutoff_occurred: bool)
        """
        visited_count[0] += 1
        if limit_guard.reached(generated_count[0]):
            return None, False

        if node.state.is_goal():
            return node, False

        if node.depth >= limit:
            return None, True  # Hit depth limit — cutoff

        cutoff_occurred = False
        for action in rules.legal_actions(node.state):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()

            # Avoid cycles within the current path
            if next_encoded in path_encoded:
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1
            )
            generated_count[0] += 1
            steps.append((
                step_num[0],
                f"[Depth {child.depth}/{limit}] Thử {action[0]} {action[1]}",
                next_state
            ))
            step_num[0] += 1

            path_encoded.add(next_encoded)
            result, cutoff = dls(child, limit, path_encoded)
            path_encoded.discard(next_encoded)

            if result is not None:
                return result, False
            if cutoff:
                cutoff_occurred = True

        return None, cutoff_occurred

    # ------------------------------------------------------------------ #
    # Outer loop — increase depth limit                                    #
    # ------------------------------------------------------------------ #
    start_node = SearchNode(start_state)
    start_encoded = start_state.encode()

    for depth_limit in range(max_depth + 1):
        steps.append((
            step_num[0],
            f"=== IDS: Bắt đầu DLS với giới hạn độ sâu = {depth_limit} ===",
            start_state
        ))
        step_num[0] += 1

        path_set = {start_encoded}
        result_node, cutoff = dls(start_node, depth_limit, path_set)

        if result_node is not None:
            actions, _ = reconstruct_path(result_node)
            steps.append((
                step_num[0],
                f"[OK] Tìm thấy lời giải! Độ sâu = {depth_limit}, Số bước = {len(actions)}",
                result_node.state
            ))
            return SearchResult(
                algorithm="IDS",
                solved=True,
                path=actions,
                visited_count=visited_count[0],
                generated_count=generated_count[0],
                elapsed_time=time.time() - start_time,
                steps=steps
            )

        if not cutoff:
            # No cutoff means all paths exhausted — no solution
            break

    return SearchResult(
        algorithm="IDS",
        solved=False,
        path=[],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps
    )
