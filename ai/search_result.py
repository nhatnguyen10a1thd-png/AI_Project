# ai/search_result.py

MAX_VISUALIZATION_STEPS = 6000


class SearchResult:
    """Standardized result returned by all AI search algorithms."""
    def __init__(self, algorithm, solved, path=None, visited_count=0, generated_count=0, elapsed_time=0.0, steps=None, extra=None):
        self.algorithm = algorithm      # Name of the algorithm (e.g. "A*", "BFS")
        self.solved = solved            # Boolean: True if solution found
        self.path = path or []          # List of actions: [(piece_id, direction), ...]
        self.visited_count = visited_count
        self.generated_count = generated_count
        self.elapsed_time = elapsed_time
        # steps: List of tuples (step_number, action_str, GameState) for visualization
        all_steps = steps or []
        self.steps_truncated = len(all_steps) > MAX_VISUALIZATION_STEPS
        self.steps = all_steps[:MAX_VISUALIZATION_STEPS]
        self.extra = extra or {}        # Extra metadata/statistics
        if self.steps_truncated:
            self.extra["steps_truncated"] = True

    def __repr__(self):
        return (f"SearchResult({self.algorithm}, solved={self.solved}, "
                f"steps={len(self.path)}, visited={self.visited_count}, "
                f"generated={self.generated_count}, time={self.elapsed_time:.4f}s)")
