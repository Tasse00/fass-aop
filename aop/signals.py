class Notifier:
    """简单实现事件订阅。避免引入blinker库"""

    def __init__(self):
        self._repo = {}

    def on(self, sig: str):
        def wrapper(handler):
            self._repo.setdefault(sig, [])
            self._repo[sig].append(handler)
            return handler

        return wrapper

    def trigger(self, sig: str, *args, **kwargs):
        handlers = self._repo.get(sig)
        for handler in handlers:
            handler(*args, **kwargs)


notifier = Notifier()

# handler(module: ModuleType)
SIG_MODULE_LOADED = 'module-loaded'

# handler(name: str, aspect: Aspect)
SIG_ASPECT_ADDED = 'aspect-added'
