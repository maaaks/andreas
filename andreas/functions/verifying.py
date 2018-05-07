import json
from typing import Dict, Iterable, Union

import rsa
from peewee import NodeList, SQL

from andreas.models.event import Event
from andreas.models.keypair import KeyPair
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.user import User


def _serialize(obj: Union[Post,Event], *, authors: Iterable[User] = None, data: Dict = None) -> bytes:
    """
    Converts given :class:`Post<andreas.models.post.Post>` or :class:`Event<andreas.models.event.Event>`
    into plain bytes so that it can be processed by ``rsa`` functions.
    
    If optional argument `data` is given, it will be used instead of the object's own data attribute.
    """
    if isinstance(obj, Post):
        j = {
            'server': str(obj.server),
            'path': obj.path,
            'authors': authors if authors is not None
                else list(str(u) for u in obj.authors()),
            'data': data if data is not None
                else obj.data,
        }
    
    if isinstance(obj, Event):
        j = {
            'server': obj.server,
            'path': obj.path,
            'authors': authors if authors is not None
                else obj.authors,
            'data': data if data is not None
                else obj.diff,
        }
    
    return json.dumps(j, sort_keys=True).encode()

def sign_post(obj: Union[Post,Event], keypair: KeyPair, **kwargs) -> bytes:
    """
    Produces RSA signature of given object `obj` using `keypair`.
    Additional arguments will be passed to :class:`_serialize()` without modification.
    """
    return rsa.sign(_serialize(obj, **kwargs), keypair.privkey, 'SHA-512')

def verify_post(obj: Union[Post,Event], user_string: str, signature: bytes, **kwargs) -> KeyPair:
    """
    Tries to verify `signature` of object `obj` using a keypair of any user that can be identified by `user_string`.
    If such keypair is found, returns it. Else, raises a ``VerificationError``.
    """
    data = _serialize(obj, **kwargs)
    
    for keypair in (KeyPair.select(KeyPair, User, Server)
        .join(User)
        .join(Server)
        .where(NodeList((User.name, SQL("|| '@' ||"), Server.name)) == user_string)
    ):
        try:
            rsa.verify(data, signature, keypair.pubkey)
            return keypair
        except rsa.VerificationError:
            pass
    
    raise rsa.VerificationError