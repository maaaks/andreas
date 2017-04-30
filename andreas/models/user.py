from datetime import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, PrimaryKeyField, fn

from andreas.db.model import Model
from andreas.models.server import Server


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