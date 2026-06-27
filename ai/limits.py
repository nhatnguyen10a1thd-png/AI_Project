import time


DEFAULT_MAX_NODES = 200000
DEFAULT_MAX_SECONDS = 10.0


class SearchLimit:
    """Shared guard that stops expensive searches before they exhaust memory."""

    def __init__(self, max_nodes=DEFAULT_MAX_NODES, max_seconds=DEFAULT_MAX_SECONDS):
        self.max_nodes = max_nodes
        self.deadline = time.perf_counter() + max_seconds

    def reached(self, nodes):
        return nodes >= self.max_nodes or time.perf_counter() >= self.deadline
