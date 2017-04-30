from typing import List

from andreas.functions.hashing import hash_post
from andreas.models.core import Event, Post, Server


def process_event(event: Event):
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
        
        # Verify hashes
        if event.hashes:
            errors = []
            for algorithm, hash in event.hashes.items():
                if hash_post(post, algorithm) != bytes.fromhex(hash):
                    errors.append(algorithm)
            if errors:
                raise IncorrectEventHashes(errors)
        
        # If no errors occured, save the post
        post.save()


class IncorrectEventHashes(Exception):
    def __init__(self, algorithms: List[str]):
        super().__init__()
        self.algorithms = algorithms
    
    def __str__(self):
        if len(self.algorithms) == 1:
            return 'Incorrect hash for {}.'.format(self.algorithms[0])
        else:
            return 'Incorrect hashes for {}.'.format(', '.join(self.algorithms))