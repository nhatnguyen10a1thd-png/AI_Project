# ai/csp/ac3.py
import time
from collections import deque

from ai.informed.heuristics import HEURISTIC_NAME, squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult
from ai.utils import action_to_text, safe_apply_action


def ac3_solve(start_state, rules, max_depth=15, max_nodes=20000, max_seconds=3.0):
    """
    AC-3 style constraint propagation over state variables S_0..S_d.

    Domain(S_i) contains states reachable in exactly i actions.  Binary arcs
    between S_i and S_{i+1} keep only values that have a legal transition
    support in the neighboring domain.  Domain(S_d) is restricted to goal
    states, then a path is reconstructed through supported transitions.  The
    heuristic is used only as a tie-breaker among remaining supported options.
    """
    start_time = time.time()
    limit = SearchLimit(max_nodes, max_seconds)
    steps = [(0, f"Khởi tạo AC-3: biến S_0..S_{max_depth}, domain là reachable states theo lớp", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    arc_checks = 0
    pruned_values = 0
    reason = "no_goal_in_depth_limit"

    if start_state.is_goal():
        return SearchResult(
            algorithm="AC-3",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps + [(step_num, "Goal ngay tại S_0", start_state)],
            extra={
                "goal_depth": 0,
                "arc_checks": 0,
                "pruned_values": 0,
                "domain_sizes": [1],
                "reason": "goal_at_start",
            },
        )

    state_cache = {start_state.encode(): start_state}
    domains = [set() for _ in range(max_depth + 1)]
    transitions = [dict() for _ in range(max_depth)]
    domains[0].add(start_state.encode())
    goal_depth = None

    for depth in range(max_depth):
        if limit.reached(generated_count):
            reason = limit.reason(generated_count) or "resource_limit"
            steps.append((step_num, f"Dừng sinh layer vì {reason}", start_state))
            step_num += 1
            break

        steps.append((step_num, f"Sinh layer S_{depth + 1} từ domain S_{depth} size={len(domains[depth])}", start_state))
        step_num += 1

        for state_code in list(domains[depth]):
            state = state_cache[state_code]
            visited_count += 1
            actions = list(rules.legal_actions(state))
            for action in actions:
                next_state = safe_apply_action(state, rules, action)
                next_code = next_state.encode()
                if next_code not in state_cache:
                    state_cache[next_code] = next_state
                    generated_count += 1
                transitions[depth].setdefault(state_code, []).append((action, next_code))
                domains[depth + 1].add(next_code)

        representative = state_cache[next(iter(domains[depth + 1]))] if domains[depth + 1] else start_state
        steps.append(
            (
                step_num,
                f"Layer S_{depth + 1}: domain_size={len(domains[depth + 1])}",
                representative,
            )
        )
        step_num += 1

        if goal_depth is None and any(state_cache[code].is_goal() for code in domains[depth + 1]):
            goal_depth = depth + 1
            steps.append((step_num, f"Phát hiện goal trong domain S_{goal_depth}", representative))
            step_num += 1
            break

    if goal_depth is None:
        return SearchResult(
            algorithm="AC-3",
            solved=False,
            path=[],
            visited_count=visited_count + arc_checks,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps,
            extra={
                "goal_depth": None,
                "arc_checks": arc_checks,
                "pruned_values": pruned_values,
                "domain_sizes": [len(domain) for domain in domains],
                "reason": reason,
            },
        )

    work_domains = [set(domains[i]) for i in range(goal_depth + 1)]
    before_goal_filter = len(work_domains[goal_depth])
    work_domains[goal_depth] = {code for code in work_domains[goal_depth] if state_cache[code].is_goal()}
    pruned_values += before_goal_filter - len(work_domains[goal_depth])
    steps.append(
        (
            step_num,
            f"Ràng buộc goal trên S_{goal_depth}: prune {before_goal_filter - len(work_domains[goal_depth])}, còn {len(work_domains[goal_depth])}",
            state_cache[next(iter(work_domains[goal_depth]))] if work_domains[goal_depth] else start_state,
        )
    )
    step_num += 1

    if not work_domains[goal_depth]:
        return SearchResult(
            algorithm="AC-3",
            solved=False,
            path=[],
            visited_count=visited_count + arc_checks,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps,
            extra={
                "goal_depth": goal_depth,
                "arc_checks": arc_checks,
                "pruned_values": pruned_values,
                "domain_sizes": [len(domain) for domain in work_domains],
                "reason": "empty_goal_domain",
            },
        )

    queue = deque()
    for index in range(goal_depth):
        queue.append((index, index + 1))
        queue.append((index + 1, index))

    def has_support(value_code, i, j):
        if j == i + 1:
            return any(next_code in work_domains[j] for _, next_code in transitions[i].get(value_code, []))
        if j == i - 1:
            for prev_code in work_domains[j]:
                if any(next_code == value_code for _, next_code in transitions[j].get(prev_code, [])):
                    return True
            return False
        return True

    def revise(i, j):
        nonlocal arc_checks, pruned_values
        removed = []
        for value_code in list(work_domains[i]):
            arc_checks += 1
            if not has_support(value_code, i, j):
                work_domains[i].remove(value_code)
                removed.append(value_code)
        pruned_values += len(removed)
        return removed

    while queue and not limit.reached(generated_count + arc_checks):
        i, j = queue.popleft()
        removed = revise(i, j)
        steps.append(
            (
                step_num,
                f"AC-3 revise arc S_{i} -> S_{j}: arc_checks={arc_checks}, pruned={len(removed)}, domain S_{i}={len(work_domains[i])}",
                state_cache[next(iter(work_domains[i]))] if work_domains[i] else start_state,
            )
        )
        step_num += 1

        if removed:
            if not work_domains[i]:
                return SearchResult(
                    algorithm="AC-3",
                    solved=False,
                    path=[],
                    visited_count=visited_count + arc_checks,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps,
                    extra={
                        "goal_depth": goal_depth,
                        "arc_checks": arc_checks,
                        "pruned_values": pruned_values,
                        "domain_sizes": [len(domain) for domain in work_domains],
                        "reason": "empty_domain",
                    },
                )

            for neighbor in (i - 1, i + 1):
                if 0 <= neighbor <= goal_depth and neighbor != j:
                    queue.append((neighbor, i))

    path = []
    current_code = start_state.encode()
    current_state = start_state

    for depth in range(goal_depth):
        options = []
        for action, next_code in transitions[depth].get(current_code, []):
            if next_code in work_domains[depth + 1]:
                options.append((squirrel_heuristic(state_cache[next_code]), action_to_text(action), action, next_code))

        if not options:
            return SearchResult(
                algorithm="AC-3",
                solved=False,
                path=[],
                visited_count=visited_count + arc_checks,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={
                    "goal_depth": goal_depth,
                    "arc_checks": arc_checks,
                    "pruned_values": pruned_values,
                    "domain_sizes": [len(domain) for domain in work_domains],
                    "reason": "reconstruction_failed",
                },
            )

        h_value, _, action, current_code = min(options, key=lambda item: (item[0], item[1]))
        current_state = state_cache[current_code]
        path.append(action)
        steps.append(
            (
                step_num,
                f"Reconstruct S_{depth}->S_{depth + 1}: chọn {action_to_text(action)} bằng tie-break h={h_value}",
                current_state,
            )
        )
        step_num += 1

    solved = current_state.is_goal()
    return SearchResult(
        algorithm="AC-3",
        solved=solved,
        path=path if solved else [],
        visited_count=visited_count + arc_checks,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "heuristic_name": HEURISTIC_NAME,
            "goal_depth": goal_depth,
            "arc_checks": arc_checks,
            "pruned_values": pruned_values,
            "domain_sizes": [len(domain) for domain in work_domains],
            "reason": "goal_found" if solved else "reconstruction_not_goal",
        },
    )
