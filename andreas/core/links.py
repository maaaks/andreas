from peewee import CharField, ForeignKeyField

from andreas.core.entry import Entry
from andreas.core.user import User
from andreas.db.model import Model


class Link_EntryToEntry(Model):
    class Meta:
        db_table = 'link_entry_to_entry'
        primary_key = False
        indexes = (
            (('entry', 'target', 'type'), True),
        )
    
    entry: Entry = ForeignKeyField(Entry, related_name='_linked_from')
    target: Entry = ForeignKeyField(Entry)
    type: str = CharField(20)


class Link_EntryToUser(Model):
    class Meta:
        db_table = 'link_entry_to_user'
        primary_key = False
        indexes = (
            (('entry', 'user', 'type'), True),
        )
    
    entry: Entry = ForeignKeyField(Entry)
    user: User = ForeignKeyField(User)
    type: str = CharField(20)


class Link_UserToEntry(Model):
    class Meta:
        db_table = 'link_user_to_entry'
        primary_key = False
        indexes = (
            (('user', 'entry', 'type'), True),
        )
    
    user: User = ForeignKeyField(User)
    entry: Entry = ForeignKeyField(Entry)
    type: str = CharField(20)