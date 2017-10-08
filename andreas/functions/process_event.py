from itertools import chain
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
                verified_signatures.append(dict(event=event, data=signature_data, keypair=keypair))
                verified_users.add(keypair.user)
            except rsa.VerificationError:
                unverified_signatures.append(dict(event=event, data=signature_data, user=user_string))
                unverified_usernames.add(user_string)
        
        # Decide whose approvals we need for this post
        required_users = { post.user }
        
        # If we got all approvals, then we save post and fill post_id in all the signatures
        success = False
        if verified_users >= required_users:
            success = True
            
            post.save()
            for signature_data in chain(verified_signatures, unverified_signatures):
                signature_data['post'] = post
            
            # If we have already analyzed this event in the past
            # but had some user's signatures unverified and now some of them became verified,
            # delete the old unverified instances
            (UnverifiedSignature.delete()
                .where(UnverifiedSignature.event == event)
                .where(UnverifiedSignature.user << [repr(u) for u in verified_users])
                .execute())
        
        # Save the signatures
        # We need them no matter what, even if we are going to raise the exception
        if verified_signatures:
            Signature.insert_many(verified_signatures).execute()
        if unverified_signatures:
            UnverifiedSignature.insert_many(unverified_signatures).execute()
        
        # Raise exception if post was not verified and therefore created/updated
        if not success:
            raise UnauthorizedAction(required_users, verified_users, unverified_usernames)


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