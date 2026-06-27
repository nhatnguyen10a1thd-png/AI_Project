# ai/informed/greedy.py
import time
import heapq
from ai.limits import SearchLimit
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult

def greedy_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """Solves the puzzle using Greedy Best-First Search (GBFS)."""
    start_time = time.time()
    
    start_node = SearchNode(start_state)
    h_start = squirrel_heuristic(start_state)
    if start_state.is_goal():
        return SearchResult(
            algorithm="Greedy",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, f"Start (h={h_start}) - Goal reached immediately", start_state)]
        )

    # Frontier is a priority queue: (h, unique_id, node)
    frontier = []
    node_counter = 0
    heapq.heappush(frontier, (h_start, node_counter, start_node))
    frontier_encoded = {start_state.encode()}
    
    explored = set()
    steps = [(0, f"Start (h={h_start})", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    limit = SearchLimit(max_nodes, max_seconds)

    while frontier:
        if limit.reached(generated_count):
            break
        h_val, _, node = heapq.heappop(frontier)
        node_encoded = node.state.encode()
        frontier_encoded.discard(node_encoded)
        explored.add(node_encoded)
        visited_count += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            return SearchResult(
                algorithm="Greedy",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps
            )

        for action in rules.legal_actions(node.state):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()

            if next_encoded not in explored and next_encoded not in frontier_encoded:
                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1,
                    depth=node.depth + 1
                )
                generated_count += 1
                h_child = squirrel_heuristic(next_state)
                steps.append((step_num, f"{action[0]} {action[1]} (h={h_child})", next_state))
                step_num += 1

                if next_state.is_goal():
                    actions, _ = reconstruct_path(child)
                    return SearchResult(
                        algorithm="Greedy",
                        solved=True,
                        path=actions,
                        visited_count=visited_count,
                        generated_count=generated_count,
                        elapsed_time=time.time() - start_time,
                        steps=steps
                    )

                node_counter += 1
                heapq.heappush(frontier, (h_child, node_counter, child))
                frontier_encoded.add(next_encoded)

    return SearchResult(
        algorithm="Greedy",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
