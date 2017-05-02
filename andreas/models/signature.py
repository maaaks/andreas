from datetime import datetime

from peewee import BlobField, DateTimeField, ForeignKeyField, PrimaryKeyField, fn

from andreas.db.model import Model
from andreas.models.keypair import KeyPair
from andreas.models.post import Post
from andreas.models.user import User


class _AbstractSignature(Model):
    """
    Base class for :class:`Signature` and :class:`UnverifiedSignature`.
    """
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    post: Post = ForeignKeyField(Post)
    """The post signed by this signature."""
    
    data: bytes = BlobField()
    """The signature itself."""

class Signature(_AbstractSignature):
    """
    Signature that verifies a post using a certain keypair.
    The user who made this signature can always be retrieved as ``keypair.user``.
    """
    class Meta:
        db_table = 'signature'
    
    keypair: KeyPair = ForeignKeyField(KeyPair)

class UnverifiedSignature(_AbstractSignature):
    """
    Signature that is supposed to verify a post but not yet checked.
    
    We know which user supposedly should have a public key that would verify this sign
    but we still have not found that public key. This means that either the sign is invalid
    or that we are not yet aware of a recently added public key to the user's profile.
    
    If one day we will find a matching public key, we will remove the `UnverifiedSignature`
    and save it as a normal :class:`Signature` instead.
    """
    class Meta:
        db_table = 'signature_unverified'
    
    user: User = ForeignKeyField(User)