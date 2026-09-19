from collections.abc import Callable


class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str):
        def decorator(func):
            if event not in self._listeners:
                self._listeners[event] = []
            self._listeners[event].append(func)
            return func

        return decorator

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args, **kwargs)


shape_events = EventEmitter()
