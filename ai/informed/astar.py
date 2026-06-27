# ai/informed/astar.py
import time
import heapq
from ai.limits import SearchLimit
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult

def astar_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """Solves the puzzle using A* Search (f = g + h)."""
    start_time = time.time()
    
    start_node = SearchNode(start_state)
    h_start = squirrel_heuristic(start_state)
    g_start = 0
    f_start = g_start + h_start
    
    if start_state.is_goal():
        return SearchResult(
            algorithm="A*",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, f"Start -> f={f_start} (g=0, h={h_start})", start_state)]
        )

    # Frontier is a priority queue: (f, unique_id, node)
    frontier = []
    node_counter = 0
    heapq.heappush(frontier, (f_start, node_counter, start_node))
    frontier_encoded = {start_state.encode()}
    
    # Store best known g-value for each state
    g_score = {start_state.encode(): g_start}
    explored = set()
    
    steps = [(0, f"Start -> f={f_start} (g={g_start}, h={h_start})", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    limit = SearchLimit(max_nodes, max_seconds)

    while frontier:
        if limit.reached(generated_count):
            break
        f_val, _, node = heapq.heappop(frontier)
        node_encoded = node.state.encode()
        frontier_encoded.discard(node_encoded)
        
        # If already popped at a lower or equal cost, skip
        if node_encoded in explored:
            continue
            
        explored.add(node_encoded)
        visited_count += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            return SearchResult(
                algorithm="A*",
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
            g_new = node.path_cost + 1

            # If we already found a shorter path to this state, ignore
            if g_new >= g_score.get(next_encoded, float('inf')):
                continue

            g_score[next_encoded] = g_new
            h_new = squirrel_heuristic(next_state)
            f_new = g_new + h_new
            
            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=g_new,
                depth=node.depth + 1
            )
            generated_count += 1
            steps.append((step_num, f"{action[0]} {action[1]} -> f={f_new} (g={g_new}, h={h_new})", next_state))
            step_num += 1

            if next_state.is_goal():
                actions, _ = reconstruct_path(child)
                return SearchResult(
                    algorithm="A*",
                    solved=True,
                    path=actions,
                    visited_count=visited_count,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps
                )

            node_counter += 1
            heapq.heappush(frontier, (f_new, node_counter, child))
            frontier_encoded.add(next_encoded)

    return SearchResult(
        algorithm="A*",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
