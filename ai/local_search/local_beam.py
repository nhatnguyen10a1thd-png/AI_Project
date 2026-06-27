# ai/local_search/local_beam.py
import time

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import SearchNode, action_to_text, reconstruct_path, safe_apply_action


def local_beam_solve(
    start_state,
    rules,
    beam_width=3,
    max_iterations=100,
    max_nodes=20000,
    max_seconds=3.0,
):
    """
    Beam-style Local Search adapted from AIMA Local Beam Search.

    Classic local beam search starts from k initial states.  This game adapter
    starts from the given puzzle state and keeps the best k successors by h(n)
    at each iteration, which is easier to demo from a fixed level.  It is not
    complete and does not guarantee an optimal plan.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    h_start = squirrel_heuristic(start_state)
    beam_width = max(1, beam_width)

    steps = [(0, f"Khởi tạo Beam-style Local Search: k={beam_width}, h_start={h_start}", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    reason = "max_iterations"
    final_best_h = h_start
    iterations_done = 0

    if start_state.is_goal():
        return SearchResult(
            algorithm="Local Beam",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại state khởi tạo", start_state)],
            extra={
                "beam_width": beam_width,
                "iterations": 0,
                "final_best_h": h_start,
                "reason": "goal_at_start",
            },
        )

    beam = [SearchNode(start_state)]
    seen = {start_state.encode()}

    for iteration in range(1, max_iterations + 1):
        iterations_done = iteration
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng Local Beam vì {reason}", beam[0].state))
            step_num += 1
            break

        beam_scores = [(squirrel_heuristic(node.state), node.depth) for node in beam]
        steps.append(
            (
                step_num,
                f"Iteration {iteration}: beam_size={len(beam)}, candidates hiện tại={beam_scores}",
                beam[0].state,
            )
        )
        step_num += 1

        candidates = []
        for node in beam:
            visited_count += 1
            legal_actions = list(rules.legal_actions(node.state))
            steps.append(
                (
                    step_num,
                    f"Mở rộng beam node depth={node.depth}, h={squirrel_heuristic(node.state)}, actions={len(legal_actions)}",
                    node.state,
                )
            )
            step_num += 1

            for action in legal_actions:
                next_state = safe_apply_action(node.state, rules, action)
                next_code = next_state.encode()
                generated_count += 1

                if next_code in seen:
                    steps.append((step_num, f"Skip {action_to_text(action)} vì repeated state", next_state))
                    step_num += 1
                    continue

                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1,
                    depth=node.depth + 1,
                )
                seen.add(next_code)
                h_child = squirrel_heuristic(next_state)
                candidates.append((h_child, child.depth, action_to_text(action), child))
                steps.append(
                    (
                        step_num,
                        f"Candidate {action_to_text(action)}: h={h_child}, depth={child.depth}",
                        next_state,
                    )
                )
                step_num += 1

                if next_state.is_goal():
                    actions, _ = reconstruct_path(child)
                    steps.append((step_num, f"Goal trong candidate, số bước={len(actions)}", next_state))
                    return SearchResult(
                        algorithm="Local Beam",
                        solved=True,
                        path=actions,
                        visited_count=visited_count,
                        generated_count=generated_count,
                        elapsed_time=time.time() - start_time,
                        steps=steps,
                        extra={
                            "heuristic_name": HEURISTIC_NAME,
                            "beam_width": beam_width,
                            "iterations": iteration,
                            "final_best_h": 0,
                            "reason": "goal_found",
                        },
                    )

        if not candidates:
            reason = "no_candidate"
            steps.append((step_num, "Dừng Local Beam vì không còn candidate mới", beam[0].state))
            step_num += 1
            break

        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        kept = candidates[:beam_width]
        beam = [child for _, _, _, child in kept]
        final_best_h = kept[0][0]
        kept_summary = [(h, depth, act) for h, depth, act, _ in kept]
        steps.append(
            (
                step_num,
                f"Giữ top-{len(beam)} theo h nhỏ nhất: {kept_summary}",
                beam[0].state,
            )
        )
        step_num += 1

    return SearchResult(
        algorithm="Local Beam",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "beam_width": beam_width,
            "iterations": iterations_done,
            "final_best_h": final_best_h,
            "reason": reason,
            "adaptation_note": "Bản demo bắt đầu từ một start_state và giữ k candidate tốt nhất.",
        },
    )
