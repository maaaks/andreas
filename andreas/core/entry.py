from datetime import datetime

from peewee import DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn
from playhouse.postgres_ext import BinaryJSONField

from andreas.core.server import Server
from andreas.db.model import Model


class Entry(Model):
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    server: Server = ForeignKeyField(Server, on_update='cascade')
    """Server where the entry originally was published and got its identification."""
    
    path: str = TextField()
    """
    Path to the query on the server, without leading slash.
    
    It is not necessary just the ``/path`` part of URL, it may include a ``?query`` part and even a ``#fragment``.
    As long as we won't mess with it, it doesn't matter for us how exactly the server's routing is done.
    """
    
    meta: str = BinaryJSONField(null=True)
    """
    Key-value container for any additional data about the entry.
    How these values are interpreted depends on implementation.
    """
    
    body: str = TextField()
    """The main content of the entry."""
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }