from datetime import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, PrimaryKeyField, fn

from andreas.db.model import Model
from andreas.models.post import Post


class PostPostRelation(Model):
    class Meta:
        db_table = 'relation_post_post'
    
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    source: Post = ForeignKeyField(Post, related_name='outgoing_relations_post_post')
    type: str = CharField()
    target: Post = ForeignKeyField(Post, related_name='incoming_relations_post_post')
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }


class UserPostRelation(Model):
    class Meta:
        db_table = 'relation_user_post'
    
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    source: Post = ForeignKeyField(Post, related_name='outgoing_relations_user_post')
    type: str = CharField()
    target: Post = ForeignKeyField(Post, related_name='incoming_relations_user_post')
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }