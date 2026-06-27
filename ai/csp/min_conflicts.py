# ai/csp/min_conflicts.py
import time
import random
from ai.search_result import SearchResult

def min_conflicts_solve(start_state, rules, k=15, max_steps=100):
    """
    Solves the puzzle using CSP Min-Conflicts.
    Variables: X_0, X_1, ..., X_k-1 (actions in a path of length k).
    Domain of X_i: All possible actions (piece_id, direction) for movable pieces.
    """
    start_time = time.time()
    
    # 1. Get all possible actions (domain)
    movable_pids = [pid for pid, p in start_state.pieces.items() if p.movable]
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    domain = [(pid, d) for pid in movable_pids for d in directions]
    
    # 2. Helper to evaluate a path and count conflicts
    def evaluate_path(path):
        current_state = start_state
        visited = {current_state.encode()}
        illegal_count = 0
        cycle_count = 0
        states_path = [current_state]
        
        goal_reached_at = -1
        
        for idx, action in enumerate(path):
            if goal_reached_at != -1:
                # Goal already reached, subsequent actions don't matter (0 conflict contribution)
                states_path.append(current_state)
                continue
                
            pid, direction = action
            if rules.can_move(current_state, pid, direction):
                current_state = rules.apply_action(current_state, action)
                enc = current_state.encode()
                if enc in visited:
                    cycle_count += 1
                visited.add(enc)
                if current_state.is_goal():
                    goal_reached_at = idx
            else:
                illegal_count += 1
            
            states_path.append(current_state)
            
        # Count active nuts in the final state
        remaining_nuts = sum(1 for p in current_state.pieces.values() if p.type == "squirrel" and p.has_nut)
        
        conflict_score = (illegal_count * 10) + (remaining_nuts * 20) + (cycle_count * 5)
        return conflict_score, states_path, goal_reached_at

    # 3. Initialize path randomly
    path = [random.choice(domain) for _ in range(k)]
    
    steps = [(0, "Min-Conflicts: Khởi tạo chuỗi hành động ngẫu nhiên", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 0

    for step in range(max_steps):
        conflict_score, states_path, goal_reached_at = evaluate_path(path)
        visited_count += 1
        
        # If no conflicts, or goal reached in the path
        if conflict_score == 0 or goal_reached_at != -1:
            # We found a path that reaches the goal!
            actual_path = path[:goal_reached_at + 1]
            actual_states = states_path[:goal_reached_at + 2]
            
            # Log the successful steps for visualization
            for idx, act in enumerate(actual_path):
                steps.append((step_num, f"Bước {idx+1}: {act[0]} {act[1]}", actual_states[idx+1]))
                step_num += 1
                
            return SearchResult(
                algorithm="Min-Conflicts",
                solved=True,
                path=actual_path,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps
            )
            
        # Log progress
        steps.append((step_num, f"Vòng {step}: Xung đột = {conflict_score}", states_path[-1]))
        step_num += 1

        # Select a random variable (step) that causes a conflict
        # A step causes a conflict if it's illegal or if it's part of the path leading to active nuts
        # We can just select a random step index
        var_idx = random.randint(0, k - 1)
        
        # Find assignment that minimizes conflicts
        best_val = path[var_idx]
        min_conflicts = conflict_score
        candidates = []
        
        for val in domain:
            path[var_idx] = val
            generated_count += 1
            score, _, _ = evaluate_path(path)
            if score < min_conflicts:
                min_conflicts = score
                candidates = [val]
            elif score == min_conflicts:
                candidates.append(val)
                
        if candidates:
            path[var_idx] = random.choice(candidates)
        else:
            path[var_idx] = best_val

    # Return whatever path we ended up with (failure)
    return SearchResult(
        algorithm="Min-Conflicts",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
