from andreas.db.database import db
from andreas.functions.hashing import hash_by_query
from andreas.models.core import Event, Post, Server


def process_event(event: Event):
    with db.atomic() as transaction:
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
            
            post.save()
        
        # Verify hashes provided in this event
        if event.hashes:
            for expression, (algorithm, hash) in event.hashes.items():
                assert hash_by_query(server, expression, algorithm) == bytes.fromhex(hash)