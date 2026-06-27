import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest

from ai.solver_interface import solve
from core.level import LevelManager
from core.rules import BoardRules


PRIMARY_SOLVERS = ["BFS", "IDS", "A*", "IDA*", "Greedy"]


def replay_path(start_state, rules, path):
    state = start_state
    for action in path:
        assert rules.can_move(state, *action), action
        state = rules.apply_action(state, action)
    return state


@pytest.mark.parametrize("algorithm_name", PRIMARY_SOLVERS)
def test_primary_solver_paths_replay_to_goal_and_do_not_mutate_start(algorithm_name):
    _, start_state = LevelManager().load_level("starter", "starter_01")
    original_key = start_state.encode()
    rules = BoardRules()

    result = solve(
        algorithm_name,
        start_state,
        rules,
        max_nodes=5000,
        max_seconds=1.0,
        max_depth=8,
        max_threshold=20,
    )

    assert start_state.encode() == original_key
    if result.solved:
        final_state = replay_path(start_state, rules, result.path)
        assert final_state.is_goal()
