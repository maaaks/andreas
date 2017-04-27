from andreas.models.core import Event, Post, Server


def process_event(event: Event):
    # Get or create the post
    try:
        post = (Post.select()
            .join(Server)
            .where(Server.hostname == event.hostname)
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