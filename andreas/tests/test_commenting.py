from andreas.functions.process_event import process_event
from andreas.functions.verifying import sign_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.relations import PostPostRelation, UserPostRelation
from andreas.models.server import Server
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class TestCommenting(AndreasTestCaseWithKeyPair):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.post = Post()
        self.post.server = self.server
        self.post.path = 'post1'
        self.post.data = {
            'body': 'How are you?',
        }
        self.post.save()
        UserPostRelation.create(source=self.abraham, type='wrote', target=self.post)
        
        event = Event()
        event.server = 'aaa'
        event.authors = ['bernard@aaa']
        event.parent = 'aaa/post1'
        event.path = 'post1#c1'
        event.data = {'body': 'Good!'}
        event.signatures = {
            'bernard@aaa': sign_post(event, self.bernard_keypair).hex(),
        }
        event.save()
        process_event(event)
    
    def test_comment_created(self):
        comment = Post.select().join(Server).where(Server.name == 'aaa', Post.path == 'post1#c1').get()
        PostPostRelation.get(
            PostPostRelation.source == comment,
            PostPostRelation.type == 'comments',
            PostPostRelation.target == self.post)