# ai/local_search/simulated_annealing.py
import time
import math
import random
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult

def simulated_annealing_solve(start_state, rules, max_iterations=500, init_temp=10.0, cooling_rate=0.95):
    """
    Solves the puzzle using Simulated Annealing.
    T starts at init_temp and drops by cooling_rate each step.
    A worse state can be accepted with probability P = exp(delta_E / T).
    """
    start_time = time.time()
    
    current_node = SearchNode(start_state)
    current_val = -squirrel_heuristic(start_state)
    
    steps = [(0, f"Start -> Value={current_val}, Temp={init_temp}", start_state)]
    step_num = 1
    visited_count = 1
    generated_count = 1
    
    if start_state.is_goal():
        return SearchResult(
            algorithm="Simulated Annealing",
            solved=True,
            path=[],
            visited_count=visited_count,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    temp = init_temp
    
    # To get repeatable results, we can seed or just let random be random.
    # We will use random.
    for i in range(1, max_iterations + 1):
        if temp < 0.01 or current_node.state.is_goal():
            break
            
        legal_actions = rules.legal_actions(current_node.state)
        if not legal_actions:
            break
            
        # Select a random action/neighbor
        action = random.choice(legal_actions)
        next_state = rules.apply_action(current_node.state, action)
        next_val = -squirrel_heuristic(next_state)
        generated_count += 1
        
        delta_e = next_val - current_val
        
        if delta_e > 0:
            # Better state, accept immediately
            current_node = SearchNode(
                state=next_state,
                parent=current_node,
                action=action,
                path_cost=current_node.path_cost + 1,
                depth=current_node.depth + 1
            )
            current_val = next_val
            visited_count += 1
            steps.append((step_num, f"[OK] Chọn {action[0]} {action[1]} (Tốt hơn) -> Value={next_val}, Temp={temp:.2f}", next_state))
            step_num += 1
        else:
            # Worse or equal state, accept with probability P = exp(delta_E / T)
            # Avoid division by zero
            prob = math.exp(delta_e / temp) if temp > 0 else 0
            if random.random() < prob:
                current_node = SearchNode(
                    state=next_state,
                    parent=current_node,
                    action=action,
                    path_cost=current_node.path_cost + 1,
                    depth=current_node.depth + 1
                )
                current_val = next_val
                visited_count += 1
                steps.append((step_num, f"[Random] Chọn {action[0]} {action[1]} (Chấp nhận xấu hơn, P={prob:.3f}) -> Value={next_val}, Temp={temp:.2f}", next_state))
                step_num += 1
            else:
                steps.append((step_num, f"Xét {action[0]} {action[1]} (Từ chối, P={prob:.3f}) -> Value={next_val}", next_state))
                step_num += 1
                
        # Cool down
        temp *= cooling_rate

    solved = current_node.state.is_goal()
    actions, _ = reconstruct_path(current_node) if solved else ([], [])
    
    return SearchResult(
        algorithm="Simulated Annealing",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
