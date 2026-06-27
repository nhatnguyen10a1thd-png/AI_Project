# ai/local_search/local_beam.py
import time

from ai.informed.heuristics import squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, reconstruct_path


def local_beam_solve(
    start_state,
    rules,
    beam_width=3,
    max_iterations=100,
    max_nodes=20000,
    max_seconds=3.0,
):
    """Solve with Local Beam Search, keeping the best k frontier states."""
    start_time = time.time()
    h_start = squirrel_heuristic(start_state)

    steps = [(0, f"Start Local Beam Search (k={beam_width}, h={h_start})", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    limit = SearchLimit(max_nodes, max_seconds)

    if start_state.is_goal():
        return SearchResult(
            algorithm="Local Beam",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps,
        )

    beam = [SearchNode(start_state)]
    seen = {start_state.encode()}

    for iteration in range(1, max_iterations + 1):
        if limit.reached(generated_count):
            break

        candidates = []
        for node in beam:
            visited_count += 1
            for action in rules.legal_actions(node.state):
                next_state = rules.apply_action(node.state, action)
                next_encoded = next_state.encode()
                if next_encoded in seen:
                    continue

                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1,
                    depth=node.depth + 1,
                )
                seen.add(next_encoded)
                generated_count += 1
                h_child = squirrel_heuristic(next_state)
                candidates.append((h_child, child.depth, child))
                steps.append(
                    (
                        step_num,
                        f"Iter {iteration}: candidate {action[0]} {action[1]} (h={h_child})",
                        next_state,
                    )
                )
                step_num += 1

                if next_state.is_goal():
                    actions, _ = reconstruct_path(child)
                    return SearchResult(
                        algorithm="Local Beam",
                        solved=True,
                        path=actions,
                        visited_count=visited_count,
                        generated_count=generated_count,
                        elapsed_time=time.time() - start_time,
                        steps=steps,
                    )

        if not candidates:
            steps.append((step_num, "No new beam candidates", beam[0].state))
            break

        candidates.sort(key=lambda item: (item[0], item[1]))
        beam = [child for _, _, child in candidates[:beam_width]]
        best_h = candidates[0][0]
        steps.append((step_num, f"Keep best {len(beam)} states for next beam (best h={best_h})", beam[0].state))
        step_num += 1

    return SearchResult(
        algorithm="Local Beam",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
    )
