from datetime import datetime

import rsa
from peewee import DateTimeField, ForeignKeyField, PrimaryKeyField, fn

from andreas.db.fields import BlobIntegerField
from andreas.db.model import Model
from andreas.models.user import User


class KeyPair(Model):
    """
    Stores information about public and (if available) private key that is known to be owned by some user.
    """
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    user: User = ForeignKeyField(User)
    
    n: int = BlobIntegerField()
    e: int = BlobIntegerField()
    d: int = BlobIntegerField(null=True)
    p: int = BlobIntegerField(null=True)
    q: int = BlobIntegerField(null=True)
    
    @property
    def privkey(self) -> rsa.PrivateKey:
        return rsa.PrivateKey(self.n, self.e, self.d, self.p, self.q)
    
    @property
    def pubkey(self) -> rsa.PublicKey:
        return rsa.PublicKey(self.n, self.e)
    
    @classmethod
    def from_privkey(cls, key: rsa.PrivateKey) -> "KeyPair":
        """Given a private key, returns a KeyPair representing all information about it."""
        return KeyPair(n=key.n, e=key.e, d=key.d, p=key.p, q=key.q)
    
    @classmethod
    def from_pubkey(cls, key: rsa.PublicKey) -> "KeyPair":
        """Given a public key, returns a KeyPair representing all information about it."""
        return KeyPair(n=key.n, e=key.e)
    
    @classmethod
    def from_file(cls, filename: str) -> "KeyPair":
        """Loads a file with either a public or private key stored in it."""
        with open(filename) as file:
            try:
                key = rsa.PrivateKey.load_pkcs1(file.read())
                return cls.from_privkey(key)
            except ValueError:
                key = rsa.PublicKey.load_pkcs1(file.read())
                return cls.from_pubkey(key)
    
    @property
    def keysize(self) -> int:
        """Returns bit length of the :data:`n` attribute."""
        return self.n.bit_length()