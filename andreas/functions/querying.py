from typing import Iterable, Optional, Union

from andreas.models.core import Post, Server


def query_posts(server: Union[Server,int], expression: str) -> Iterable[Post]:
    """
    Searches the given `server` for posts according to conditions specified in the `expression`.
    
    Supported expressions are:
        - `=/post1` — gets exactly one post, with path `/post1`
    """
    if expression[:1] == '=':
        try:
            yield Post.get(Post.server == server, Post.path == expression[1:])
        except Post.DoesNotExist:
            pass

def query_post(server: Union[Server,int], expression: str) -> Optional[Post]:
    """
    Searches the given `server` for a single post according to conditions specified in the `expression`.
    Accepts only the ``=``-queries.
    """
    assert expression[:1] == '='
    for post in query_posts(server, expression):
        return post
    return None