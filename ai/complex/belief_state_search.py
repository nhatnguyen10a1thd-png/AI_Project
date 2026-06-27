# ai/complex/belief_state_search.py
import time
from collections import deque
from ai.search_result import SearchResult

def belief_state_solve(start_state, rules, max_states=1000):
    """
    Solves the puzzle using Belief-State Search (Partial Observability).
    The initial belief state contains multiple possible states (e.g., the exact anchor
    of the block/flower is unknown; it could be in a couple of neighboring positions).
    Finds a single sequence of actions that solves the game for all possible states.
    """
    start_time = time.time()
    
    # 1. Construct initial belief state
    # Let's assume the exact initial position of the "flower" or a blocker is uncertain
    # We will generate 3 possible initial states by moving the "flower" if possible.
    initial_states = [start_state]
    
    if "flower" in start_state.pieces:
        flower = start_state.pieces["flower"]
        original_anchor = flower.anchor
        
        # Look for a couple of nearby empty cells to place the flower and create alternative initial states
        alt_anchors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            test_anchor = (original_anchor[0] + dr, original_anchor[1] + dc)
            # Check if this cell is free
            cell_free = True
            for pid, p in start_state.pieces.items():
                if pid == "flower":
                    continue
                if test_anchor in p.occupied_cells():
                    cell_free = False
                    break
            # Must be inside bounds
            if 0 <= test_anchor[0] < 4 and 0 <= test_anchor[1] < 4 and cell_free:
                alt_anchors.append(test_anchor)
                if len(alt_anchors) >= 2:
                    break
                    
        for anc in alt_anchors:
            alt_state = start_state.clone()
            alt_state.pieces["flower"].anchor = anc
            initial_states.append(alt_state)
            
    # Belief state is a frozenset of hashable state encodings
    # To keep GameState objects accessible, we'll store a dict mapping encoding -> GameState
    state_cache = {s.encode(): s for s in initial_states}
    initial_belief = frozenset(state_cache.keys())
    
    # Check if goal is already met for all states in initial belief
    def is_belief_goal(belief):
        return all(state_cache[se].is_goal() for se in belief)
        
    steps = [(0, f"Belief State: Khởi tạo với {len(initial_belief)} trạng thái khả thi", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    
    if is_belief_goal(initial_belief):
        return SearchResult(
            algorithm="Belief-State",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    # BFS on belief states
    # Queue stores (belief_state, path_actions)
    queue = deque([(initial_belief, [])])
    explored_beliefs = {initial_belief}

    # Find list of movable piece IDs
    movable_pids = [pid for pid, p in start_state.pieces.items() if p.movable]
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    actions_domain = [(pid, d) for pid in movable_pids for d in directions]

    solution_path = []
    solved = False

    while queue and len(explored_beliefs) < max_states:
        curr_belief, path = queue.popleft()
        visited_count += 1
        
        # Log belief state stats
        rep_state = state_cache[next(iter(curr_belief))]
        steps.append((step_num, f"Duyệt Belief State (Cỡ={len(curr_belief)}) | Bước={len(path)}", rep_state))
        step_num += 1

        if is_belief_goal(curr_belief):
            solution_path = path
            solved = True
            break

        # Try actions
        for act in actions_domain:
            pid, direction = act
            
            # Compute next belief state
            next_belief_list = []
            valid_action_for_all = True
            
            for se in curr_belief:
                s = state_cache[se]
                # If action is legal in this state
                if rules.can_move(s, pid, direction):
                    ns = rules.apply_action(s, act)
                    nse = ns.encode()
                    if nse not in state_cache:
                        state_cache[nse] = ns
                    next_belief_list.append(nse)
                else:
                    # Action is illegal for at least one state in the belief state
                    valid_action_for_all = False
                    break
            
            if not valid_action_for_all:
                continue
                
            next_belief = frozenset(next_belief_list)
            
            if next_belief not in explored_beliefs:
                explored_beliefs.add(next_belief)
                generated_count += 1
                queue.append((next_belief, path + [act]))

    # If solved, log the solution steps for visualization
    if solved:
        curr_state = start_state
        for idx, act in enumerate(solution_path):
            curr_state = rules.apply_action(curr_state, act)
            steps.append((step_num, f"Bước {idx+1}: {act[0]} {act[1]}", curr_state))
            step_num += 1

    return SearchResult(
        algorithm="Belief-State",
        solved=solved,
        path=solution_path,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={"belief_states_searched": len(explored_beliefs)}
    )
