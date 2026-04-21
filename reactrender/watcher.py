"""
pyreactssr/watcher.py

Lightweight file watcher that clears the engine's bundle cache whenever
a file inside frontend_dir changes. Works without watchdog — uses a
background thread with os.stat polling.
"""
import os
import threading
import time
from typing import Callable


class FrontendWatcher:
    """
    Polls frontend_dir for file changes and calls `on_change(path)` on each hit.

    Usage:
        watcher = FrontendWatcher("./frontend/src", on_change=lambda p: print("changed:", p))
        watcher.start()
        # later:
        watcher.stop()
    """

    EXTENSIONS = {".tsx", ".ts", ".jsx", ".js", ".css", ".svg", ".png", ".jpg"}

    def __init__(
        self,
        watch_dir: str,
        on_change: Callable[[str], None],
        poll_interval: float = 0.4,
    ):
        self.watch_dir = os.path.abspath(watch_dir)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._mtimes: dict[str, float] = {}
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the background polling thread."""
        self._snapshot()  # seed initial mtimes
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the watcher to stop."""
        self._stop_event.set()

    # ------------------------------------------------------------------

    def _loop(self):
        while not self._stop_event.is_set():
            self._check()
            time.sleep(self.poll_interval)

    def _snapshot(self):
        for path in self._walk():
            try:
                self._mtimes[path] = os.path.getmtime(path)
            except OSError:
                pass

    def _check(self):
        current: dict[str, float] = {}
        for path in self._walk():
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            current[path] = mtime
            old = self._mtimes.get(path)
            if old is None or mtime != old:
                self._mtimes[path] = mtime
                self.on_change(path)

        # detect deletions
        deleted = set(self._mtimes) - set(current)
        for p in deleted:
            del self._mtimes[p]
            self.on_change(p)

    def _walk(self):
        for root, _, files in os.walk(self.watch_dir):
            for name in files:
                if any(name.endswith(ext) for ext in self.EXTENSIONS):
                    yield os.path.join(root, name)
