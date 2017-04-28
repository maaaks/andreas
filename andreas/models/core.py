from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

from peewee import BooleanField, CharField, Check, DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn
from playhouse.postgres_ext import BinaryJSONField

from andreas.db.model import Model


class Server(Model):
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    hostname: str = TextField()
    engine_name: str = CharField(50, null=True)
    engine_version: str = CharField(50, null=True)
    
    is_local: bool = BooleanField(default=False)
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }
    
    @classmethod
    @lru_cache(1)
    def local(cls) -> "Server":
        return cls.get(Server.is_local == True)


class Event(Model):
    id: int = PrimaryKeyField()
    received: datetime = DateTimeField(default=fn.now)
    
    received_from: Server = ForeignKeyField(Server, null=True, on_update='cascade')
    """
    Server that we got this Event from.
    In general, this has nothing to do with which server produced the event originally.
    """
    
    hostname: str = TextField()
    """
    Hostname of the server on which the post affected by this event is published.
    """
    
    path: str = TextField(null=True)
    """
    Identification of the post affected by this event.
    This is the same path as in :data:`Post.path`.
    """
    
    diff: Dict[str,Any] = BinaryJSONField(default={}, constraints=[Check("jsonb_typeof(diff) = 'object'")])
    """
    Changes which should be applied to the post.
    """
    
    hashes: Dict[str,str] = BinaryJSONField(default={}, constraints=[Check("jsonb_typeof(hashes) = 'object'")])
    """
    Actual hashes that the author wants to provide or update.
    The hashes should be provided as dictionary where each key is an expression
    and value is a two-element array containing algorithm name
    and the hash of the post/list specified by that expression.
    """


class Post(Model):
    class Meta:
        indexes = (
            (('server', 'path'), True),
        )
    
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    server: Server = ForeignKeyField(Server, on_update='cascade')
    """Server where the post was originally published and got its identification."""
    
    path: str = TextField()
    """
    Path to the query on the server, without leading slash.
    
    It is not necessary just the ``/path`` part of URL, it may include a ``?query`` part and even a ``#fragment``.
    As long as we won't mess with it, it doesn't matter for us how exactly the server's routing is done.
    """
    
    data: Dict[str,Any] = BinaryJSONField(default={}, constraints=[Check("jsonb_typeof(data) = 'object'")])
    """
    The entire content of the post in JSON format.
    How some of the values are interpreted may depend on implementation.
    """
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }


class User(Model):
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    server: Server = ForeignKeyField(Server, on_update='cascade')
    """Server where this user is registered."""
    
    login: str = CharField(50)
    """User's identification on its server."""
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }