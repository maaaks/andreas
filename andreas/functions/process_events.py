from typing import Dict, List

import rsa

from andreas.functions.verifying import verify_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.signature import Signature, UnverifiedSignature
from andreas.models.user import User


def process_event(event: Event):
    server: Server = Server.get(Server.name == event.server)
    
    # Create or update the post with data provided in this event
    if event.path:
        try:
            post = (Post.select()
                .where(Post.server == server)
                .where(Post.path == event.path)
                .get())
        except Post.DoesNotExist:
            post = Post()
            post.server = Server.get(Server.name == event.server)
            post.path = event.path
        
        # Add/replace elements from the event,
        # remove elements which are nulls in the information provided by event
        for key, value in event.diff.items():
            if value is not None:
                post.data[key] = value
            else:
                del post.data[key]
        
        # The event has signatures, right?
        if not event.signatures:
            raise NoSignaturesProvided
        
        # Verify signatures
        # If at least one signature is ok, consider the post verified
        verified_signatures: List[Dict] = []
        unverified_signatures: List[Dict] = []
        for user_string, signature_data in event.signatures.items():
            user = User.from_string(user_string, create=True)
            try:
                keypair = verify_post(post, user, bytes.fromhex(signature_data))
                verified_signatures.append(dict(post=post, data=signature_data, keypair=keypair))
            except rsa.VerificationError:
                unverified_signatures.append(dict(post=post, data=signature_data, user=user))
        
        # If we couldn't verify any signature at all, reject the post
        if not verified_signatures:
            raise CouldNotVerifySignatures
        
        # Else, save the post and all the signatures
        post.save()
        Signature.insert_many(verified_signatures).execute()
        if unverified_signatures:
            UnverifiedSignature.insert_many(unverified_signatures).execute()

class NoSignaturesProvided(Exception):
    pass

class CouldNotVerifySignatures(Exception):
    pass