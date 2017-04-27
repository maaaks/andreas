from datetime import datetime

from lxml import etree
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn
from playhouse.postgres_ext import BinaryJSONField

from andreas.db.fields import XmlField
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


class Event(Model):
    id: int = PrimaryKeyField()
    received: datetime = DateTimeField(default=fn.now)
    
    received_from: Server = ForeignKeyField(Server, on_update='cascade')
    """
    Server that we got this Event from.
    In general, this has nothing to do with which server produced the event originally.
    """
    
    path: str = TextField()
    """
    Identification of the post affected by this event.
    This is the same path as in :data:`Post.path`.
    """
    
    xpath: str = TextField()
    """
    Path of the XML element which will be deleted or added/replaced with content from :data:`xml`.
    """
    
    xml: etree.ElementBase = XmlField()
    """
    If `NULL`, this means that the element specified by :data:`xpath` should be removed from the post.
    Else, the element should be added (or replaced) with the content provided here.
    """


class Post(Model):
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
    
    meta: str = BinaryJSONField(null=True)
    """
    Key-value container for any additional data about the post.
    How these values are interpreted depends on implementation.
    """
    
    body: str = TextField()
    """The main content of the post."""
    
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