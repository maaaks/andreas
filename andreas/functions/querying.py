from typing import Iterable, List, Tuple, Type, Union

from peewee import CTE, NodeList, SQL, SelectQuery

from andreas.models.post import Post
from andreas.models.relations import PostPostRelation
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
    server, path = identifier.split('/', maxsplit=1)
    return get_post(server, path)


def get_comments_list(post: Union[Post,int]) -> List[Tuple[Post,int]]:
    """
    Given a `post`, recursively loads all comments for it.
    The comments which are on a same level are shown in chronological order.
    The comments which are replies to another comment are shown below it immediately.
    
    The implementation uses `recursion <http://docs.peewee-orm.com/en/latest/peewee/query_examples.html#recursion>`_.
    
    :return: A list of tuples. Each tuple contains a comment and its level in the discussion.
    """
    Comment: Type[Post] = Post.alias()
    Subcomment: Type[Post] = Post.alias()
    
    comments: CTE = (Comment
        .select(
            NodeList((SQL('array['), Comment.created, SQL(']'))).alias('_breadcrumbs'),
            Comment)
        .join(PostPostRelation, on=PostPostRelation.source)
        .where(PostPostRelation.type == 'comments')
        .where(PostPostRelation.target == post)
        .cte('t', recursive=True))
    
    subcomments: SelectQuery = (Subcomment
        .select(
            NodeList((comments.c._breadcrumbs, SQL('|| array['), Subcomment.created, SQL(']'))).alias('_breadcrumbs'),
            Subcomment)
        .join(PostPostRelation, on=((PostPostRelation.source == Subcomment.id) & (PostPostRelation.type == 'comments')))
        .join(comments, on=(PostPostRelation.target == comments.c.id)))
    
    cte: CTE = comments.union_all(subcomments)
    query: Iterable[Post] = (cte
        .select_from(
            *(getattr(cte.c, column) for column in Post._meta.columns.keys()),
            cte.c._breadcrumbs)
        .order_by(cte.c._breadcrumbs))
    
    return list((p, p._breadcrumbs) for p in query)