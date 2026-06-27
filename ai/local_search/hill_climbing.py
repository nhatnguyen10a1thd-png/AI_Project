# ai/local_search/hill_climbing.py
import time
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult

def hill_climbing_solve(start_state, rules):
    """
    Solves the puzzle using Simple Hill Climbing.
    Value(state) = -h(state) (higher is better).
    Stops when it reaches a local optimum or goal.
    """
    start_time = time.time()
    
    current_node = SearchNode(start_state)
    current_val = -squirrel_heuristic(start_state)
    
    steps = [(0, f"Start -> Value={current_val}", start_state)]
    step_num = 1
    visited_count = 1
    generated_count = 1
    
    if start_state.is_goal():
        return SearchResult(
            algorithm="Hill Climbing",
            solved=True,
            path=[],
            visited_count=visited_count,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    while True:
        legal_actions = rules.legal_actions(current_node.state)
        found_better = False
        
        for action in legal_actions:
            next_state = rules.apply_action(current_node.state, action)
            next_val = -squirrel_heuristic(next_state)
            generated_count += 1
            
            steps.append((step_num, f"Xét {action[0]} {action[1]} -> Value={next_val}", next_state))
            step_num += 1

            if next_val > current_val:
                # Found a better state, move to it immediately (Simple Hill Climbing)
                current_node = SearchNode(
                    state=next_state,
                    parent=current_node,
                    action=action,
                    path_cost=current_node.path_cost + 1,
                    depth=current_node.depth + 1
                )
                current_val = next_val
                visited_count += 1
                
                steps.append((step_num, f"[OK] Chọn {action[0]} {action[1]} -> Value={next_val}", next_state))
                step_num += 1
                
                found_better = True
                break
                
        # If no neighbor is strictly better, we stop (stuck at local optimum)
        if not found_better:
            steps.append((step_num, f"[X] Kẹt cục bộ (Value={current_val})", current_node.state))
            step_num += 1
            break
            
        if current_node.state.is_goal():
            break

    solved = current_node.state.is_goal()
    actions, _ = reconstruct_path(current_node) if solved else ([], [])
    
    return SearchResult(
        algorithm="Hill Climbing",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
