from typing import Dict, List, Set

import rsa

from andreas.functions.verifying import verify_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.signature import Signature, UnverifiedSignature
from andreas.models.user import User


def process_event(event: Event):
    server: Server = Server.get(Server.name == event.server)
    user: User = User.from_string(event.user)
    
    # Create or update the post with data provided in this event
    if event.path:
        try:
            post = (Post.select()
                .where(Post.server == server)
                .where(Post.path == event.path)
                .where(Post.user == user)
                .get())
        except Post.DoesNotExist:
            post = Post()
            post.server = Server.get(Server.name == event.server)
            post.user = user
            post.path = event.path
        
        # Add/replace elements from the event,
        # remove elements which are nulls in the information provided by event
        for key, value in event.diff.items():
            if value is not None:
                post.data[key] = value
            elif key in post.data:
                del post.data[key]
        
        verified_signatures: List[Dict] = []
        unverified_signatures: List[Dict] = []
        verified_users: Set[User] = set()
        unverified_usernames: Set[str] = set()
        
        # Try to verify and save as many signatures as possible
        for user_string, signature_hex in event.signatures.items():
            signature_data = bytes.fromhex(signature_hex)
            try:
                keypair = verify_post(post, user_string, signature_data)
                verified_signatures.append(dict(post=post, data=signature_data, keypair=keypair))
                verified_users.add(keypair.user)
            except rsa.VerificationError:
                unverified_signatures.append(dict(post=post, data=signature_data, user=user_string, event=event))
                unverified_usernames.add(user_string)
        
        # Decide whose approvals we need for this post
        required_users = { post.user }
        
        # Make sure that we've got all signatures we need
        if not required_users <= verified_users:
            # Save all verified signatures, but set post=None because the Post isn't saved
            verified_signatures = map(lambda d: dict(x for x in d.items() if x[0]!='post'), verified_signatures)
            Signature.insert_many(verified_signatures).execute()
            
            # Do the same with unverified signatures
            unverified_signatures = map(lambda d: dict(x for x in d.items() if x[0]!='post'), unverified_signatures)
            UnverifiedSignature.insert_many(unverified_signatures).execute()
            
            # Exception indicates that we haven't saved the post itself, only the signatures
            raise UnauthorizedAction(required_users, verified_users, unverified_usernames)
        
        # Else, save the post and all the signature
        post.save()
        Signature.insert_many(verified_signatures).execute()
        UnverifiedSignature.insert_many(unverified_signatures).execute()

class UnauthorizedAction(Exception):
    def __init__(self, required_users: Set[User], verified_users: Set[User], unverified_usernames: Set[str]):
        super().__init__()
        self.required_users: Set[User] = required_users
        self.verified_users: Set[User] = verified_users
        self.unverified_usernames: Set[str] = unverified_usernames
    
    def __str__(self):
        missing_users = self.required_users - self.verified_users
        missing_users_list = ', '.join(sorted(map(str, missing_users)))
        msg = f'Missing authorization by {missing_users_list}.'
        
        if self.unverified_usernames:
            unverified_usernames_list = ', '.join(sorted(self.unverified_usernames))
            msg += f'\n  Note: Failed to verify {unverified_usernames_list}.'
        
        return msg