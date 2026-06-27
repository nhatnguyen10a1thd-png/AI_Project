# ai/complex/belief_state_search.py
import time
from collections import deque

from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import action_to_text, safe_apply_action


def belief_state_solve(start_state, rules, max_states=1000, max_seconds=3.0):
    """
    Conformant belief-state BFS from AIMA, adapted to Squirrels Go Nuts.

    A belief state is a set of possible GameState encodings.  This demo builds
    an initial belief by allowing the flower/blocker to be in a few neighboring
    positions.  It then searches for one action sequence that works for every
    possible state.  There is no percept update after each action.
    """
    start_time = time.time()
    limit = SearchLimit(max_states, max_seconds)

    def build_initial_belief():
        possible = [start_state]
        if "flower" not in start_state.pieces:
            return possible

        flower = start_state.pieces["flower"]
        original_anchor = flower.anchor
        alternatives = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            test_anchor = (original_anchor[0] + dr, original_anchor[1] + dc)
            if not (0 <= test_anchor[0] < 4 and 0 <= test_anchor[1] < 4):
                continue
            if any(
                pid != "flower" and test_anchor in piece.occupied_cells()
                for pid, piece in start_state.pieces.items()
            ):
                continue
            alt_state = start_state.clone()
            alt_state.pieces["flower"].anchor = test_anchor
            alternatives.append(alt_state)
            if len(alternatives) >= 2:
                break
        possible.extend(alternatives)
        return possible

    initial_states = build_initial_belief()
    state_cache = {state.encode(): state for state in initial_states}
    initial_belief = frozenset(state_cache.keys())

    steps = [
        (
            0,
            f"Khởi tạo Belief-State BFS: initial_belief_size={len(initial_belief)}, conformant_plan=True",
            start_state,
        )
    ]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reason = "max_states"

    for index, possible_state in enumerate(initial_states, start=1):
        steps.append((step_num, f"Possible initial state {index}/{len(initial_states)}", possible_state))
        step_num += 1

    def is_belief_goal(belief):
        return all(state_cache[state_code].is_goal() for state_code in belief)

    if is_belief_goal(initial_belief):
        return SearchResult(
            algorithm="Belief-State",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Mọi possible state đều là goal", start_state)],
            extra={
                "initial_belief_size": len(initial_belief),
                "belief_states_searched": 1,
                "conformant_plan": True,
                "reason": "goal_at_start",
            },
        )

    movable_ids = [pid for pid, piece in start_state.pieces.items() if piece.movable]
    actions_domain = [(pid, direction) for pid in movable_ids for direction in ("UP", "DOWN", "LEFT", "RIGHT")]

    queue = deque([(initial_belief, [])])
    explored_beliefs = {initial_belief}
    solution_path = []
    solved = False

    while queue:
        if limit.reached(len(explored_beliefs)):
            reason = limit.reason(len(explored_beliefs)) or "resource_limit"
            steps.append((step_num, f"Dừng Belief-State vì {reason}", start_state))
            step_num += 1
            break

        belief, path = queue.popleft()
        visited_count += 1
        representative = state_cache[next(iter(belief))]
        steps.append(
            (
                step_num,
                f"Mở rộng belief size={len(belief)}, path_len={len(path)}, queue còn={len(queue)}",
                representative,
            )
        )
        step_num += 1

        if is_belief_goal(belief):
            solution_path = path
            solved = True
            reason = "goal_belief_found"
            steps.append((step_num, "Found belief goal: mọi state trong belief đều đạt goal", representative))
            step_num += 1
            break

        for action in actions_domain:
            next_belief_codes = []
            invalid_state = None

            for state_code in belief:
                state = state_cache[state_code]
                if not rules.can_move(state, *action):
                    invalid_state = state
                    break
                next_state = safe_apply_action(state, rules, action)
                next_code = next_state.encode()
                state_cache.setdefault(next_code, next_state)
                next_belief_codes.append(next_code)

            if invalid_state is not None:
                steps.append(
                    (
                        step_num,
                        f"Skip {action_to_text(action)} vì illegal trong một possible state",
                        invalid_state,
                    )
                )
                step_num += 1
                continue

            next_belief = frozenset(next_belief_codes)
            steps.append(
                (
                    step_num,
                    f"Thử {action_to_text(action)} -> next_belief_size={len(next_belief)}",
                    state_cache[next(iter(next_belief))],
                )
            )
            step_num += 1

            if next_belief in explored_beliefs:
                steps.append((step_num, f"Skip belief lặp sau {action_to_text(action)}", state_cache[next(iter(next_belief))]))
                step_num += 1
                continue

            explored_beliefs.add(next_belief)
            generated_count += 1
            queue.append((next_belief, path + [action]))

    if solved:
        replay_state = start_state
        for index, action in enumerate(solution_path, start=1):
            replay_state = safe_apply_action(replay_state, rules, action)
            steps.append((step_num, f"Replay plan step {index}: {action_to_text(action)}", replay_state))
            step_num += 1
    elif reason == "max_states" and not queue:
        reason = "frontier_empty"

    return SearchResult(
        algorithm="Belief-State",
        solved=solved,
        path=solution_path,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "initial_belief_size": len(initial_belief),
            "belief_states_searched": len(explored_beliefs),
            "conformant_plan": True,
            "reason": reason,
        },
    )
