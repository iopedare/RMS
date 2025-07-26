import threading

class SyncTasks:
    """
    Background task scheduler for periodic sync and retry logic.
    Schedules periodic sync every 30 seconds and handles retries for failed syncs.
    """
    def __init__(self, sync_manager):
        self.sync_manager = sync_manager
        self.timer = None

    def start_periodic_sync(self):
        """Start the periodic sync task (every 30 seconds)."""
        self._schedule_next_sync()

    def _schedule_next_sync(self):
        self.timer = threading.Timer(30.0, self._run_sync)
        self.timer.start()

    def _run_sync(self):
        self.sync_manager.periodic_sync()
        self._schedule_next_sync()

    def stop(self):
        """Stop the periodic sync task."""
        if self.timer:
            self.timer.cancel() 