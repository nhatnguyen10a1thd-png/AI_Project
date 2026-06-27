# ai/complex/online_search.py
import time

from ai.informed.heuristics import squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, reconstruct_path


def online_search_solve(start_state, rules, max_steps=200, max_nodes=20000, max_seconds=3.0):
    """
    Online search using an LRTA* style update.

    The agent repeatedly senses only the current state's legal successors,
    updates its learned heuristic for the current state, and moves to the
    neighbor with the lowest estimated cost.
    """
    start_time = time.time()
    steps = [(0, "Start Online Search (LRTA* style)", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    limit = SearchLimit(max_nodes, max_seconds)

    if start_state.is_goal():
        return SearchResult(
            algorithm="Online Search",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps,
        )

    learned_h = {start_state.encode(): squirrel_heuristic(start_state)}
    revisit_count = {start_state.encode(): 1}
    current_node = SearchNode(start_state)

    for _ in range(max_steps):
        if current_node.state.is_goal() or limit.reached(generated_count):
            break

        current_code = current_node.state.encode()
        successors = []
        visited_count += 1

        for action in rules.legal_actions(current_node.state):
            next_state = rules.apply_action(current_node.state, action)
            next_code = next_state.encode()
            if next_code not in learned_h:
                learned_h[next_code] = squirrel_heuristic(next_state)
            estimate = 1 + learned_h[next_code]
            successors.append((estimate, learned_h[next_code], action, next_state, next_code))
            generated_count += 1

        if not successors:
            steps.append((step_num, "No legal successor from current state", current_node.state))
            break

        successors.sort(key=lambda item: (item[0], item[1]))
        learned_h[current_code] = successors[0][0]
        estimate, h_next, action, next_state, next_code = successors[0]

        current_node = SearchNode(
            state=next_state,
            parent=current_node,
            action=action,
            path_cost=current_node.path_cost + 1,
            depth=current_node.depth + 1,
        )
        revisit_count[next_code] = revisit_count.get(next_code, 0) + 1
        steps.append(
            (
                step_num,
                f"Online move {action[0]} {action[1]} (learned cost={estimate}, h_next={h_next})",
                next_state,
            )
        )
        step_num += 1

        if revisit_count[next_code] > 8 and not next_state.is_goal():
            steps.append((step_num, "Stopped after repeated visits to the same state", next_state))
            break

    solved = current_node.state.is_goal()
    actions, _ = reconstruct_path(current_node) if solved else ([], [])

    return SearchResult(
        algorithm="Online Search",
        solved=solved,
        path=actions,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={"learned_states": len(learned_h)},
    )
