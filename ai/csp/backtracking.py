# ai/csp/backtracking.py
import time
from ai.search_result import SearchResult
from ai.limits import SearchLimit

def backtracking_solve(start_state, rules, max_depth=15, max_nodes=20000, max_seconds=3.0):
    """
    Solves the puzzle using CSP Backtracking Search.
    Finds a sequence of actions of length <= max_depth that leads to the goal state.
    """
    start_time = time.time()
    steps = [(0, "Start Backtracking Search", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    limit = SearchLimit(max_nodes, max_seconds)
    
    if start_state.is_goal():
        return SearchResult(
            algorithm="Backtracking",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    visited_states = {start_state.encode()}
    
    def backtrack(state, path):
        visited_count[0] += 1
        if limit.reached(generated_count[0]):
            return None
        
        if state.is_goal():
            return path
            
        if len(path) >= max_depth:
            return None
            
        legal_actions = rules.legal_actions(state)
        for action in legal_actions:
            next_state = rules.apply_action(state, action)
            next_encoded = next_state.encode()
            
            if next_encoded not in visited_states:
                generated_count[0] += 1
                steps.append((step_num[0], f"Thử {action[0]} {action[1]} (bước {len(path)+1}/{max_depth})", next_state))
                step_num[0] += 1
                
                visited_states.add(next_encoded)
                sol = backtrack(next_state, path + [action])
                if sol is not None:
                    return sol
                
                # Undo / Backtrack
                visited_states.remove(next_encoded)
                steps.append((step_num[0], f"Quay lui {action[0]} {action[1]}", state))
                step_num[0] += 1
                
        return None

    solution_path = backtrack(start_state, [])
    solved = solution_path is not None
    
    return SearchResult(
        algorithm="Backtracking",
        solved=solved,
        path=solution_path or [],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps
    )
