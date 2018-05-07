from datetime import datetime
from typing import Union

from peewee import BlobField, DateTimeField, ForeignKeyField, PrimaryKeyField, TextField, fn

from andreas.db.model import Model
from andreas.models.event import Event
from andreas.models.keypair import KeyPair
from andreas.models.post import Post


class Signature(Model):
    """
    Signature that verifies a post using a certain keypair.
    The user who made this signature can always be retrieved as ``keypair.user``.
    
    The field :data:`post` can contain `NULL` if the :data:`event` was rejected,
    for example when the provided signatures were valid but not authorized to perform the action.
    """
    class Meta:
        table_name = 'signature'
    
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    event: Event = ForeignKeyField(Event)
    keypair: KeyPair = ForeignKeyField(KeyPair)
    post: Union[ForeignKeyField,Post] = ForeignKeyField(Post, null=True)
    data: bytes = BlobField()


class UnverifiedSignature(Model):
    """
    Signature that is supposed to verify a post but not yet checked.
    
    The worst case scenario here is that the signature is corrupted or just made by someone else,
    and so we are destined to store this unverified signature forever without ability to confirm it.
    
    But that's not the only case. Maybe we just use an outdated profile database
    and therefore don't know yet that the user identified by `user_string` added a new public key.
    After we will eventually update his profile, we will revalidate all signatures that have his username
    and, probably, will be able to apply some of previously rejected events.
    If it happens, we will delete the ``UnverifiedSignature`` and save the same data as a normal :class:`Signature`.
    
    It's important that there is a small possibility that user who currently has given username
    has nothing to do with the user who signed the message long time ago.
    (This depends on a server's policy about how nicknames are managed and how users are being deleted.)
    That's why even if we have a user with matching the user name in our database,
    we must not reference them from any messages until we will find the missing public key.
    Only a public key can be a proof that certain user said certain things, not a username without a key.
    
    Just like :class:`Signature`, this class can contain `NULL` in :data:`post`
    because the :data:`event` that contained an unverified signature
    could easily end up being rejected and not produce a :class:`Post`.
    """
    class Meta:
        table_name = 'signature_unverified'
    
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    event: Event = ForeignKeyField(Event)
    user: str = TextField()
    post: Union[ForeignKeyField,Post] = ForeignKeyField(Post, null=True)
    data: bytes = BlobField()