from datetime import datetime
from typing import Any, Dict

from peewee import Check, DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn
from playhouse.postgres_ext import BinaryJSONField

from andreas.db.model import Model
from andreas.models.server import Server


class Event(Model):
    id: int = PrimaryKeyField()
    received: datetime = DateTimeField(default=fn.now)
    
    received_from: Server = ForeignKeyField(Server, null=True, on_update='cascade')
    """
    Server that we got this Event from.
    In general, this has nothing to do with which server produced the event originally.
    """
    
    server: str = TextField()
    """
    Name of the server on which the post affected by this event is published.
    """
    
    user: str = TextField()
    """
    Name of the user who should be the «owner» of the post.
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
    
    signatures: Dict[str,str] = BinaryJSONField(default={}, constraints=[Check("jsonb_typeof(signatures) = 'object'")])
    """
    RSA signatures of the resulting post after the diff is applied.
    The event may contain signatures by different users, even from different servers.
    Each key is full user identification (see :meth:`User::from_string()<andreas.models.user.User.from_string>`),
    and each value is the sign made by that user.
    """