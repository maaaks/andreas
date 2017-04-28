import hashlib
import json
from typing import Union, Iterable

from andreas.functions.querying import query_post, query_posts_paths
from andreas.models.core import Post, Server


def hash_post(post: Post, algorithm: str) -> bytes:
    h = hashlib.new(algorithm)
    h.update(json.dumps(post.data, sort_keys=True).encode())
    return h.digest()

def hash_post_by_query(server: Union[Server,int], expression: str, algorithm: str) -> bytes:
    return hash_post(query_post(server, expression), algorithm)

def hash_posts_list(paths: Iterable[str], algorithm: str) -> bytes:
    h = hashlib.new(algorithm)
    h.update(b'\n'.join(map(bytes, paths)))
    return h.digest()

def hash_posts_list_by_query(server: Union[Server,int], expression: str, algorithm: str) -> bytes:
    return hash_posts_list(query_posts_paths(server, expression), algorithm)

def hash_by_query(server: Union[Server,int], expression: str, algorithm: str) -> bytes:
    if expression[:1] == '=':
        return hash_post_by_query(server, expression, algorithm)
    else:
        return hash_posts_list_by_query(server, expression, algorithm)