# ai/solver_interface.py
import inspect

from ai.uninformed.bfs import bfs_solve
from ai.uninformed.dfs import dfs_solve
from ai.uninformed.ids import ids_solve
from ai.informed.greedy import greedy_solve
from ai.informed.astar import astar_solve
from ai.informed.idastar import idastar_solve
from ai.local_search.hill_climbing import hill_climbing_solve
from ai.local_search.local_beam import local_beam_solve
from ai.local_search.simulated_annealing import simulated_annealing_solve
from ai.csp.ac3 import ac3_solve
from ai.csp.backtracking import backtracking_solve
from ai.csp.min_conflicts import min_conflicts_solve
from ai.adversarial.minimax import minimax_solve
from ai.adversarial.alpha_beta import alphabeta_solve
from ai.adversarial.expectimax import expectimax_solve
from ai.complex.and_or_search import and_or_solve
from ai.complex.belief_state_search import belief_state_solve
from ai.complex.online_search import online_search_solve

# Danh sách thuật toán theo bảng yêu cầu:
# 1. Tìm kiếm mù      → BFS, DFS, IDS
# 2. Heuristic Search  → A*, IDA*, Greedy
# 3. Local Search      → Hill Climbing, Local Beam, Simulated Annealing
# 4. Adversarial       → Minimax, Alpha-Beta, Expectimax
# 5. CSP               → AC-3, Backtracking, Min-Conflicts
# 6. Complex           -> AND-OR Search, Belief-State, Online Search
ALGORITHMS = {
    "BFS":                 bfs_solve,
    "DFS":                 dfs_solve,
    "IDS":                 ids_solve,
    "A*":                  astar_solve,
    "IDA*":                idastar_solve,
    "Greedy":              greedy_solve,
    "Hill Climbing":       hill_climbing_solve,
    "Local Beam":          local_beam_solve,
    "Simulated Annealing": simulated_annealing_solve,
    "Minimax":             minimax_solve,
    "Alpha-Beta":          alphabeta_solve,
    "Expectimax":          expectimax_solve,
    "AC-3":                ac3_solve,
    "Backtracking":        backtracking_solve,
    "Min-Conflicts":       min_conflicts_solve,
    "AND-OR Search":       and_or_solve,
    "Belief-State":        belief_state_solve,
    "Online Search":       online_search_solve,
}


def solve(algorithm_name, start_state, rules, **kwargs):
    """
    Uniform solve function.
    algorithm_name: key from ALGORITHMS (e.g. "A*", "BFS")
    start_state: GameState
    rules: BoardRules
    """
    if algorithm_name not in ALGORITHMS:
        raise ValueError(
            f"Unknown algorithm: {algorithm_name}. Supported: {list(ALGORITHMS.keys())}"
        )

    solve_func = ALGORITHMS[algorithm_name]
    supported = inspect.signature(solve_func).parameters
    filtered_kwargs = {key: value for key, value in kwargs.items() if key in supported}
    result = solve_func(start_state, rules, **filtered_kwargs)

    # Never expose a solver path that cannot be replayed by the game controls.
    if result.solved:
        state = start_state
        for action in result.path:
            if not rules.can_move(state, *action):
                result.solved = False
                result.path = []
                result.extra["invalid_solution_path"] = True
                break
            state = rules.apply_action(state, action)
        if result.solved and not state.is_goal():
            result.solved = False
            result.path = []
            result.extra["invalid_solution_path"] = True
    return result
