from datetime import datetime

from peewee import BooleanField, CharField, DateTimeField, PrimaryKeyField, TextField, fn

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