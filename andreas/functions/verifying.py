import json
from typing import Dict, Union

import rsa
from peewee import Clause, SQL

from andreas.models.event import Event
from andreas.models.keypair import KeyPair
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.user import User


def _serialize(obj: Union[Post,Event], data: Dict = None) -> bytes:
    """
    Converts given :class:`Post<andreas.models.post.Post>` or :class:`Event<andreas.models.event.Event>`
    into plain bytes so that it can be processed by ``rsa`` functions.
    
    If optional argument `data` is given, it will be used instead of the object's own data attribute.
    """
    if isinstance(obj, Post):
        return json.dumps({
            'data': data or obj.data,
            'user': str(obj.user),
            'server': str(obj.server) if obj.server else None,
            'path': obj.path,
        }, sort_keys=True).encode()
    
    if isinstance(obj, Event):
        return json.dumps({
            'data': data or obj.diff,
            'user': obj.user,
            'server': obj.server,
            'path': obj.path,
        }, sort_keys=True).encode()

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
        .where(Clause(User.name, SQL("|| '@' ||"), Server.name) == user_string)
    ):
        try:
            rsa.verify(data, signature, keypair.pubkey)
            return keypair
        except rsa.VerificationError:
            pass
    
    raise rsa.VerificationError