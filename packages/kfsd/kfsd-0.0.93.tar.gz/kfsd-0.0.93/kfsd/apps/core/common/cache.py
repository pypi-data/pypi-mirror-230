from django.core.cache import cache as DjangoCache
from functools import wraps


def cache(key, timeout=3600):
    def get(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = DjangoCache.get(key)
            if data is None:
                data = func(*args, **kwargs)
                DjangoCache.set(key, data, timeout)
            return data

        return wrapper

    return get
