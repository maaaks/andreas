from typing import Union

from andreas.models.post import Post
from andreas.models.server import Server


def get_post(server: Union[Server,str,int], path: str) -> Post:
    """
    Returns a post with given `path` on given `server`.
    
    :param server: The :class:`Server<andreas.models.core.Server>` object, or its id, or its name.
    :param path: The path to the required :class:`Post<andreas.models.core.Post>` on the server.
    """
    if isinstance(server, str):
        return Post.select(Post, Server).join(Server).where(Server.name == server).where(Post.path == path).get()
    else:
        return Post.get(Post.server == server, Post.path == path)


def get_post_by_identifier(identifier: str) -> Post:
    server, path = identifier.split('/')
    return get_post(server, '/'+path)