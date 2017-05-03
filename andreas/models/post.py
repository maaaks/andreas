from datetime import datetime
from typing import Any, Dict

from peewee import Check, DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn
from playhouse.postgres_ext import BinaryJSONField

from andreas.db.model import Model
from andreas.models.server import Server
from andreas.models.user import User


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
    
    user: User = ForeignKeyField(User, on_update='cascade')
    """Author of the entry."""
    
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