import time


DEFAULT_MAX_NODES = 200000
DEFAULT_MAX_SECONDS = 10.0


class SearchLimit:
    """Shared guard that stops expensive searches before they exhaust memory."""

    def __init__(self, max_nodes=DEFAULT_MAX_NODES, max_seconds=DEFAULT_MAX_SECONDS):
        self.max_nodes = max_nodes
        self.max_seconds = max_seconds
        self.start_time = time.perf_counter()
        self.deadline = time.perf_counter() + max_seconds

    def reached(self, nodes):
        return nodes >= self.max_nodes or time.perf_counter() >= self.deadline

    def reason(self, nodes):
        """Return a stable reason string when the guard has been reached."""
        if nodes >= self.max_nodes:
            return "max_nodes"
        if time.perf_counter() >= self.deadline:
            return "max_seconds"
        return None
