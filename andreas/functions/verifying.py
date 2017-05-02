import json
from typing import Union

import rsa

from andreas.models.keypair import KeyPair
from andreas.models.post import Post
from andreas.models.user import User


def verify_post(post: Post, user: Union[User,int], signature: bytes) -> KeyPair:
    """
    Checks whether given `data` could be a valid signature of the `post` with any one of `user`'s keypairs.
    If such keypair is found, returns it. Else, raises a ``VerificationError``.
    """
    data = json.dumps(post.data, sort_keys=True).encode()
    
    for keypair in KeyPair.select().where(KeyPair.user == user):  # type: KeyPair
        try:
            rsa.verify(data, signature, keypair.pubkey)
            return keypair
        except rsa.VerificationError:
            pass
    
    raise rsa.VerificationError