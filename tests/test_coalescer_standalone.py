"""Standalone test of the decorator-freeze coalescer algorithm from tree.py.
Mirrors request_decorator_freeze/_on_decorator_freeze_job/_freeze_decorator_now
with a fake clock + fake cron to verify burst behavior."""

import math

DECORATOR_COALESCE_MS = 16

class FakeCron:
    def __init__(self, clock):
        self.clock = clock
        self.jobs = {}
        self.next_id = 0

    def after(self, interval, fn):
        ms = int(interval.replace("ms", ""))
        self.next_id += 1
        self.jobs[self.next_id] = (self.clock.now + ms / 1000, fn)
        return self.next_id

    def cancel(self, job_id):
        self.jobs.pop(job_id, None)

    def advance_to(self, t):
        while True:
            due = [(jid, at, fn) for jid, (at, fn) in self.jobs.items() if at <= t]
            if not due:
                break
            due.sort(key=lambda x: x[1])
            jid, at, fn = due[0]
            del self.jobs[jid]
            self.clock.now = at
            fn()
        self.clock.now = t

class Clock:
    def __init__(self):
        self.now = 100.0

class FakeTree:
    def __init__(self, clock, cron):
        self.clock = clock
        self.cron = cron
        self.freezes = []
        self.canvas_decorator = True
        self.destroying = False
        self._decorator_freeze_pending_job = None
        self._last_decorator_freeze_ts = 0.0

    def request_decorator_freeze(self):
        if not self.canvas_decorator or self.destroying:
            return
        if self._decorator_freeze_pending_job:
            return
        elapsed_ms = (self.clock.now - self._last_decorator_freeze_ts) * 1000
        if elapsed_ms >= DECORATOR_COALESCE_MS:
            self._freeze_decorator_now()
        else:
            delay = max(1, math.ceil(DECORATOR_COALESCE_MS - elapsed_ms))
            self._decorator_freeze_pending_job = self.cron.after(f"{delay}ms", self._on_decorator_freeze_job)

    def _on_decorator_freeze_job(self):
        self._decorator_freeze_pending_job = None
        if self.canvas_decorator and not self.destroying:
            self._freeze_decorator_now()

    def _freeze_decorator_now(self):
        if self._decorator_freeze_pending_job:
            self.cron.cancel(self._decorator_freeze_pending_job)
            self._decorator_freeze_pending_job = None
        self._last_decorator_freeze_ts = self.clock.now
        self.freezes.append(self.clock.now)

def run():
    failures = []

    def check(name, expect, actual):
        ok = expect == actual
        print(f"{'PASS' if ok else 'FAIL'}: {name} (expect {expect}, got {actual})")
        if not ok:
            failures.append(name)

    # 1. isolated event freezes immediately
    clock = Clock(); cron = FakeCron(clock); tree = FakeTree(clock, cron)
    tree.request_decorator_freeze()
    check("isolated event freezes immediately", 1, len(tree.freezes))

    # 2. burst of 10 highlight calls in 5ms -> 1 immediate + 1 trailing
    for i in range(10):
        clock.now += 0.0005
        tree.request_decorator_freeze()
    cron.advance_to(clock.now + 0.05)
    check("burst of 10 in 5ms -> 2 freezes total", 2, len(tree.freezes))

    # 3. sustained 180 calls/sec for 1s -> ~62 freezes max
    clock = Clock(); cron = FakeCron(clock); tree = FakeTree(clock, cron)
    t0 = clock.now
    for i in range(180):
        cron.advance_to(t0 + i / 180)
        tree.request_decorator_freeze()
    cron.advance_to(t0 + 1.1)
    check("180 calls over 1s coalesce to <= 63 freezes", True, len(tree.freezes) <= 63)
    check("180 calls over 1s still repaint >= 55 times", True, len(tree.freezes) >= 55)

    # 4. trailing freeze always lands (no lost repaint)
    clock = Clock(); cron = FakeCron(clock); tree = FakeTree(clock, cron)
    tree.request_decorator_freeze()          # immediate
    clock.now += 0.001
    tree.request_decorator_freeze()          # inside window -> schedules
    check("second request pending, not yet frozen", 1, len(tree.freezes))
    cron.advance_to(clock.now + 0.1)
    check("trailing freeze fired", 2, len(tree.freezes))

    # 5. pipeline freeze cancels pending job, no double repaint
    clock = Clock(); cron = FakeCron(clock); tree = FakeTree(clock, cron)
    tree.request_decorator_freeze()
    clock.now += 0.001
    tree.request_decorator_freeze()          # schedules trailing
    tree._freeze_decorator_now()             # pipeline freeze arrives
    cron.advance_to(clock.now + 0.1)
    check("pipeline freeze absorbs pending job", 2, len(tree.freezes))

    # 6. destroyed tree never freezes
    clock = Clock(); cron = FakeCron(clock); tree = FakeTree(clock, cron)
    tree.request_decorator_freeze()
    clock.now += 0.001
    tree.request_decorator_freeze()
    tree.destroying = True
    cron.advance_to(clock.now + 0.1)
    check("no freeze after destroy", 1, len(tree.freezes))

    print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILURES: {failures}"))
    return not failures

if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
