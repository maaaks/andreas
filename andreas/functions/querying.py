from typing import Union

from andreas.models.post import Post
from andreas.models.server import Server


def get_post(server: Union[Server,str,int], path: str) -> Post:
    """
    Returns a post with given `path` on given `server`.
    
    :param server: The :class:`Server<andreas.models.core.Server>` object, or its id, or its hostname.
    :param path: The path to the required :class:`Post<andreas.models.core.Post>` on the server.
    """
    if isinstance(server, str):
        return Post.select(Post, Server).join(Server).where(Server.hostname == server).where(Post.path == path).get()
    else:
        return Post.get(Post.server == server, Post.path == path)