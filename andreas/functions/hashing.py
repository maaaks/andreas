import hashlib
import json

from andreas.models.core import Post


def hash_post(post: Post, algorithm: str) -> bytes:
    h = hashlib.new(algorithm)
    h.update(json.dumps(post.data, sort_keys=True).encode())
    return h.digest()