# ai/informed/idastar.py
import time

from ai.informed.heuristics import squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, reconstruct_path


def idastar_solve(
    start_state,
    rules,
    max_depth=60,
    max_threshold=120,
    max_nodes=20000,
    max_seconds=3.0,
):
    """Solve with Iterative Deepening A* (IDA*), using f = g + h thresholds."""
    start_time = time.time()
    h_start = squirrel_heuristic(start_state)

    steps = [(0, f"Start IDA* (h={h_start})", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    limit = SearchLimit(max_nodes, max_seconds)

    if start_state.is_goal():
        return SearchResult(
            algorithm="IDA*",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps,
        )

    def search(node, threshold, path_encoded):
        visited_count[0] += 1
        h_val = squirrel_heuristic(node.state)
        f_val = node.path_cost + h_val

        if f_val > threshold:
            return f_val, None
        if node.state.is_goal():
            return f_val, node
        if node.depth >= max_depth or limit.reached(generated_count[0]):
            return float("inf"), None

        actions = []
        for action in rules.legal_actions(node.state):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()
            if next_encoded in path_encoded:
                continue
            h_child = squirrel_heuristic(next_state)
            actions.append((node.path_cost + 1 + h_child, h_child, action, next_state, next_encoded))

        actions.sort(key=lambda item: (item[0], item[1]))
        min_next_threshold = float("inf")

        for child_f, h_child, action, next_state, next_encoded in actions:
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1,
            )
            generated_count[0] += 1
            steps.append(
                (
                    step_num[0],
                    f"{action[0]} {action[1]} -> f={child_f} (g={child.path_cost}, h={h_child}, limit={threshold})",
                    next_state,
                )
            )
            step_num[0] += 1

            path_encoded.add(next_encoded)
            overrun, result = search(child, threshold, path_encoded)
            path_encoded.remove(next_encoded)

            if result is not None:
                return overrun, result
            min_next_threshold = min(min_next_threshold, overrun)

        return min_next_threshold, None

    root = SearchNode(start_state)
    threshold = h_start
    start_encoded = start_state.encode()

    while threshold <= max_threshold and not limit.reached(generated_count[0]):
        steps.append((step_num[0], f"IDA*: new iteration with threshold={threshold}", start_state))
        step_num[0] += 1

        next_threshold, result_node = search(root, threshold, {start_encoded})
        if result_node is not None:
            actions, _ = reconstruct_path(result_node)
            steps.append((step_num[0], f"Found solution at cost={len(actions)}", result_node.state))
            return SearchResult(
                algorithm="IDA*",
                solved=True,
                path=actions,
                visited_count=visited_count[0],
                generated_count=generated_count[0],
                elapsed_time=time.time() - start_time,
                steps=steps,
            )

        if next_threshold == float("inf"):
            break
        threshold = next_threshold

    return SearchResult(
        algorithm="IDA*",
        solved=False,
        path=[],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={"last_threshold": threshold},
    )
