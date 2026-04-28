"""In-memory cache for storing query results and answers."""
import hashlib

_CACHE = {}


def make_key(user_id: int, question: str) -> str:
    """Create a cache key from user_id and question."""
    combined = f"{user_id}:{question}".lower()
    return hashlib.md5(combined.encode()).hexdigest()


def get(key: str):
    """Get value from cache by key."""
    return _CACHE.get(key)


def set(key: str, value, ttl: int | None = None):
    """Set value in cache. Note: ttl is ignored in this simple in-memory implementation."""
    _CACHE[key] = value


def get_answer(user_id: int, question: str):
    """Get cached answer for a user's question, or None if not cached."""
    key = make_key(user_id, question)
    return get(key)


def set_answer(user_id: int, question: str, answer: str):
    """Cache an answer for a user's question."""
    key = make_key(user_id, question)
    set(key, answer)


def clear():
    """Clear all cached items."""
    global _CACHE
    _CACHE = {}


def stats():
    """Return cache statistics."""
    return {"size": len(_CACHE), "keys": list(_CACHE.keys())}
