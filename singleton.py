from threading import Lock


class SingletonMeta(type):

    def __init__(cls, *args, **kwargs):
        super(SingletonMeta, cls).__init__(*args, **kwargs)
        cls._instance = None
        cls._lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            instance = cls._instance
            if instance is None:
                instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                cls._instance = instance
        return instance
