# ai/csp/ac3.py
import time
from collections import deque

from ai.informed.heuristics import squirrel_heuristic
from ai.limits import SearchLimit
from ai.search_result import SearchResult


def ac3_solve(start_state, rules, max_depth=15, max_nodes=20000, max_seconds=3.0):
    """
    AC-3 style constraint propagation over state variables S_0..S_d.

    Each S_i domain contains states reachable in exactly i moves. Binary arcs
    between S_i and S_{i+1} keep only states that have a legal transition to a
    still-possible neighbor. The final variable is restricted to goal states.
    """
    start_time = time.time()
    steps = [(0, "Start AC-3 over reachable state layers", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    arc_checks = 0
    pruned_values = 0
    limit = SearchLimit(max_nodes, max_seconds)

    if start_state.is_goal():
        return SearchResult(
            algorithm="AC-3",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps,
        )

    state_cache = {start_state.encode(): start_state}
    domains = [set() for _ in range(max_depth + 1)]
    transitions = [dict() for _ in range(max_depth)]
    domains[0].add(start_state.encode())
    goal_depth = None

    for depth in range(max_depth):
        if limit.reached(generated_count):
            break

        for state_code in list(domains[depth]):
            state = state_cache[state_code]
            visited_count += 1
            for action in rules.legal_actions(state):
                next_state = rules.apply_action(state, action)
                next_code = next_state.encode()
                if next_code not in state_cache:
                    state_cache[next_code] = next_state
                    generated_count += 1
                transitions[depth].setdefault(state_code, []).append((action, next_code))
                domains[depth + 1].add(next_code)

        steps.append(
            (
                step_num,
                f"Layer {depth + 1}: domain size={len(domains[depth + 1])}",
                state_cache[next(iter(domains[depth + 1]))] if domains[depth + 1] else start_state,
            )
        )
        step_num += 1

        if goal_depth is None and any(state_cache[code].is_goal() for code in domains[depth + 1]):
            goal_depth = depth + 1
            break

    if goal_depth is None:
        return SearchResult(
            algorithm="AC-3",
            solved=False,
            path=[],
            visited_count=visited_count,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps,
            extra={"reason": "no_goal_in_depth_limit"},
        )

    work_domains = [set(domains[i]) for i in range(goal_depth + 1)]
    work_domains[goal_depth] = {code for code in work_domains[goal_depth] if state_cache[code].is_goal()}

    queue = deque()
    for i in range(goal_depth):
        queue.append((i, i + 1))
        queue.append((i + 1, i))

    def has_support(value_code, i, j):
        if j == i + 1:
            return any(next_code in work_domains[j] for _, next_code in transitions[i].get(value_code, []))

        if j == i - 1:
            return any(
                prev_code in work_domains[j] and any(next_code == value_code for _, next_code in transitions[j].get(prev_code, []))
                for prev_code in work_domains[j]
            )

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
        return bool(removed)

    while queue and not limit.reached(generated_count):
        i, j = queue.popleft()
        if revise(i, j):
            steps.append((step_num, f"AC-3 revised arc S{i}<->S{j}, domain S{i}={len(work_domains[i])}", start_state))
            step_num += 1

            if not work_domains[i]:
                return SearchResult(
                    algorithm="AC-3",
                    solved=False,
                    path=[],
                    visited_count=visited_count + arc_checks,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps,
                    extra={"reason": "empty_domain", "pruned_values": pruned_values},
                )

            for neighbor in (i - 1, i + 1):
                if 0 <= neighbor <= goal_depth and neighbor != j:
                    queue.append((neighbor, i))

    path = []
    current_code = start_state.encode()
    current_state = start_state

    for depth in range(goal_depth):
        options = [
            (squirrel_heuristic(state_cache[next_code]), action, next_code)
            for action, next_code in transitions[depth].get(current_code, [])
            if next_code in work_domains[depth + 1]
        ]
        if not options:
            return SearchResult(
                algorithm="AC-3",
                solved=False,
                path=[],
                visited_count=visited_count + arc_checks,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps,
                extra={"reason": "reconstruction_failed", "pruned_values": pruned_values},
            )

        _, action, current_code = min(options, key=lambda item: item[0])
        current_state = state_cache[current_code]
        path.append(action)
        steps.append((step_num, f"AC-3 path step {depth + 1}: {action[0]} {action[1]}", current_state))
        step_num += 1

    return SearchResult(
        algorithm="AC-3",
        solved=current_state.is_goal(),
        path=path if current_state.is_goal() else [],
        visited_count=visited_count + arc_checks,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={"goal_depth": goal_depth, "arc_checks": arc_checks, "pruned_values": pruned_values},
    )
