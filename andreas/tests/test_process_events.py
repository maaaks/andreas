from andreas.functions.process_events import UnauthorizedAction, process_event
from andreas.functions.verifying import sign_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class TestCreatePost(AndreasTestCaseWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'Hello, World!',
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        self.event.signatures = {
            'abraham@aaa': sign_post(self.event, self.abraham_keypair).hex(),
        }
        self.event.save()
        process_event(self.event)
    
    def test_all(self):
        post: Post = (Post.select()
            .join(Server)
            .where(Server.name == 'aaa')
            .where(Post.path == '/post1')
            .get())
        self.assertEqual(self.event.diff, post.data)

class TestModifyPost(AndreasTestCaseWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.post = Post()
        self.post.server = self.server
        self.post.user = self.abraham
        self.post.path = '/post1'
        self.post.data = {
            'title': 'Hello',
            'subtitle': 'A hello world post',
            'body': 'Hello, World!',
        }
        self.post.save()
        
        event = Event()
        event.server = 'aaa'
        event.user = 'abraham@aaa'
        event.path = '/post1'
        event.diff = {
            'title': 'Hello (updated)',
            'subtitle': None,
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        event.signatures = {
            'abraham@aaa': sign_post(event, self.abraham_keypair, data={
                'title': 'Hello (updated)',
                'body': 'Hello, World!',
                'tags': ['Aaa', 'Bbb', 'Ccc'],
            }).hex(),
        }
        event.save()
        process_event(event)
        
        self.post.reload()
    
    def test_title_updated(self):
        self.assertEqual('Hello (updated)', self.post.data['title'])
    
    def test_subtitle_removed(self):
        self.assertFalse('subtitle' in self.post.data)
    
    def test_body_untouched(self):
        self.assertEqual('Hello, World!', self.post.data['body'])
    
    def test_tags_added(self):
        self.assertEqual(['Aaa', 'Bbb', 'Ccc'], self.post.data['tags'])

class TestIncorrectSignature(AndreasTestCaseWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'This event should be rejected.',
        }
        self.event.signatures = {
            'abraham@aaa': sign_post(self.event, self.abraham_keypair).hex(),
        }
        self.event.save()
    
    def test_all(self):
        with self.assertRaisesRegex(UnauthorizedAction, 'Missing authorization by abraham@aaa.'):
            process_event(self.event)

class TestUnauthorizedAction(AndreasTestCaseWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'This event should be rejected.',
        }
        self.event.signatures = {
            'bernard@aaa': sign_post(self.event, self.abraham_keypair).hex(),
        }
        self.event.save()
    
    def test_all(self):
        with self.assertRaisesRegex(UnauthorizedAction, 'Missing authorization by abraham@aaa.'):
            process_event(self.event)