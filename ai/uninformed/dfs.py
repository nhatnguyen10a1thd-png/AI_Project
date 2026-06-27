# ai/uninformed/dfs.py
import time

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, reconstruct_path


def dfs_solve(start_state, rules, max_depth=40, max_nodes=20000, max_seconds=3.0):
    """Solve the puzzle using Depth-First Search with a depth guard."""
    start_time = time.time()

    if start_state.is_goal():
        return SearchResult(
            algorithm="DFS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, "Start (goal reached immediately)", start_state)],
        )

    start_node = SearchNode(start_state)
    stack = [start_node]
    frontier_encoded = {start_state.encode()}
    explored = set()
    limit = SearchLimit(max_nodes, max_seconds)

    steps = [(0, f"Start DFS (max_depth={max_depth})", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1

    while stack:
        if limit.reached(generated_count):
            break

        node = stack.pop()
        node_encoded = node.state.encode()
        frontier_encoded.discard(node_encoded)

        if node_encoded in explored:
            continue

        explored.add(node_encoded)
        visited_count += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            return SearchResult(
                algorithm="DFS",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
            )

        if node.depth >= max_depth:
            steps.append((step_num, f"Depth limit reached at depth={node.depth}", node.state))
            step_num += 1
            continue

        actions = list(rules.legal_actions(node.state))
        for action in reversed(actions):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()

            if next_encoded in explored or next_encoded in frontier_encoded:
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1,
            )
            generated_count += 1
            steps.append(
                (
                    step_num,
                    f"Push {action[0]} {action[1]} (depth={child.depth})",
                    next_state,
                )
            )
            step_num += 1

            if next_state.is_goal():
                actions, _ = reconstruct_path(child)
                return SearchResult(
                    algorithm="DFS",
                    solved=True,
                    path=actions,
                    visited_count=visited_count,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps,
                )

            stack.append(child)
            frontier_encoded.add(next_encoded)

    return SearchResult(
        algorithm="DFS",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
    )
