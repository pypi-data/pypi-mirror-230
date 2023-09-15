import time
from collections import defaultdict
from navconfig.logging import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flowtask.exceptions import ComponentError
from .watch import BaseWatcher, BaseWatchdog


# TODO> PatternMatchingEventHandler

fslog = logging.getLogger('watchdog.observers')
fslog.setLevel(logging.WARNING)


class fsHandler(FileSystemEventHandler):
    def __init__(self, parent: BaseWatchdog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debounced_events = defaultdict(lambda: 0)
        self.parent = parent

    def on_any_event(self, event):
        if event.is_directory:
            return None

        # Check if an event for this path has been triggered recently
        last_event_time = self.debounced_events[event.src_path]
        current_time = time.time()
        if current_time - last_event_time < 0.5:  # 0.5 seconds debounce time
            return

        self.debounced_events[event.src_path] = current_time

        if event.event_type == 'created':
            print(f"Watchdog received created event - {event.src_path} s.")
            self.parent.call_actions()
        elif event.event_type == 'modified':
            print(f"Watchdog received modified event - {event.src_path} s.")
            self.parent.call_actions()
        elif event.event_type == 'deleted':
            print(f"Watchdog received deleted event - {event.src_path} s.")
            self.parent.call_actions()
        elif event.event_type == 'moved':
            print(f"Watchdog received moved event - {event.src_path} s.")
            self.parent.call_actions()

class fsWatcher(BaseWatcher):
    def __init__(self, *args, **kwargs):
        super(fsWatcher, self).__init__(*args, **kwargs)
        self.directory = kwargs.pop('directory', None)
        self.recursive = kwargs.pop('recursive', True)
        self.observer = Observer()

    def run(self):
        event_handler = fsHandler(self.parent)
        self.observer.schedule(
            event_handler,
            self.directory,
            recursive=self.recursive
        )
        self.observer.start()
        try:
            while True:
                time.sleep(self.timeout)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Watchdog FS Observer was stopped")
            self.observer.join()

    def stop(self):
        try:
            self.observer.stop()
        except Exception:
            pass
        self.observer.join()

class FSWatchdog(BaseWatchdog):
    """FSWatchdog.
        Checking for changes in the filesystem and dispatch events.
    """
    timeout: int = 5
    recursive: bool = True

    def create_watcher(self, *args, **kwargs) -> BaseWatcher:
        self.recursive = kwargs.pop('recursive', True)
        try:
            self.directory = kwargs['directory']
        except KeyError as exc:
            raise ComponentError(
                "Unable to load Directory on FSWatchdog"
            ) from exc
        return fsWatcher(
            directory=self.directory,
            timeout=self.timeout,
            recursive=self.recursive
        )
