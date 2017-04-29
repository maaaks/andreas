from typing import List, Tuple

from andreas.db.database import db
from andreas.functions.hashing import hash_by_query
from andreas.models.core import Event, Post, Server


def process_event(event: Event):
    with db.atomic():
        server: Server = Server.get(Server.hostname == event.hostname)
        
        # Create or update the post with data provided in this event
        if event.path:
            try:
                post = (Post.select()
                    .where(Post.server == server)
                    .where(Post.path == event.path)
                    .get())
            except Post.DoesNotExist:
                post = Post()
                post.server = Server.get(Server.hostname == event.hostname)
                post.path = event.path
            
            # Add/replace elements from the event,
            # remove elements which are nulls in the information provided by event
            for key, value in event.diff.items():
                if value is not None:
                    post.data[key] = value
                else:
                    del post.data[key]
            
            # Save the post (this will be rollbacked if hashes won't match)
            post.save()
        
        # Verify hashes provided in this event
        if event.hashes:
            errors = []
            for expression, (algorithm, hash) in event.hashes.items():
                if hash_by_query(server, expression, algorithm) != bytes.fromhex(hash):
                    errors.append((expression, hash))
            
            # If one or mre hashes are incorrect, rollbackk the changes
            if errors:
                raise IncorrectEventHashes(errors)


class IncorrectEventHashes(Exception):
    def __init__(self, errors: List[Tuple[str,str]]):
        super().__init__()
        self.errors = errors
    
    def __str__(self):
        msg = 'Incorrect hashes:'
        for query, hash in self.errors:
            msg += '\n  `{}` is not {}'.format(query, hash)
        return msg