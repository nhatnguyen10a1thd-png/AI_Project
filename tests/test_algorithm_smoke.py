import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai.search_result import SearchResult
from ai.solver_interface import ALGORITHMS, solve
from core.level import LevelManager
from core.rules import BoardRules


def run_smoke():
    _, start_state = LevelManager().load_level("starter", "starter_01")
    rules = BoardRules()
    kwargs = {
        "max_nodes": 1000,
        "max_seconds": 0.5,
        "max_depth": 4,
        "max_threshold": 20,
        "max_iterations": 20,
        "max_steps": 20,
        "max_moves": 4,
        "max_states": 100,
        "k": 6,
        "seed": 0,
    }

    for algorithm_name in ALGORITHMS:
        result = solve(algorithm_name, start_state, rules, **kwargs)
        assert isinstance(result, SearchResult), algorithm_name
        assert isinstance(result.path, list), algorithm_name
        assert result.steps, algorithm_name
        assert result.visited_count >= 0, algorithm_name
        assert result.generated_count >= 0, algorithm_name
        assert isinstance(result.extra, dict), algorithm_name
        print(
            f"{algorithm_name}: solved={result.solved}, "
            f"path={len(result.path)}, visited={result.visited_count}, generated={result.generated_count}"
        )


if __name__ == "__main__":
    run_smoke()
