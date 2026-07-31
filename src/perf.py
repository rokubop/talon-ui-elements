import time
from collections import defaultdict

class PerfCounters:
    """Lightweight always-on counters for the render hot paths.
    Snapshot with actions.user.ui_elements_perf_stats() from the REPL."""
    def __init__(self):
        self.counters = defaultdict(int)
        self.durations_ms = defaultdict(float)
        self.started = time.monotonic()

    def count(self, name: str):
        self.counters[name] += 1

    def add_duration(self, name: str, ms: float):
        self.counters[name] += 1
        self.durations_ms[name] += ms

    def reset(self):
        self.counters.clear()
        self.durations_ms.clear()
        self.started = time.monotonic()

    def stats(self) -> dict:
        elapsed = max(time.monotonic() - self.started, 1e-9)
        result = {"elapsed_s": round(elapsed, 2)}
        for name in sorted(self.counters):
            count = self.counters[name]
            entry = {
                "count": count,
                "per_s": round(count / elapsed, 1),
            }
            if name in self.durations_ms:
                entry["avg_ms"] = round(self.durations_ms[name] / count, 3)
                entry["total_ms"] = round(self.durations_ms[name], 1)
            result[name] = entry
        return result

perf = PerfCounters()
