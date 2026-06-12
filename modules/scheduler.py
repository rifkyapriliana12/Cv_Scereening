import schedule
import time
import threading
import logging
from datetime import datetime
from typing import Callable, Optional

class Scheduler:
    def __init__(self):
        self.job = None
        self.running = False
        self.thread = None

    def run_daily_at_2359(self, task_func: Callable):
        schedule.every().day.at("23:59").do(task_func)
        print(f"[SCHEDULER] Task scheduled for 23:59 daily")

    def run_now(self, task_func: Callable):
        print(f"[SCHEDULER] Running task now ({datetime.now().strftime('%H:%M')})")
        task_func()

    def start(self):
        def _loop():
            self.running = True
            while self.running:
                schedule.run_pending()
                time.sleep(30)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()
        print("[SCHEDULER] Scheduler started in background")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[SCHEDULER] Scheduler stopped")
