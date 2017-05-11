from andreas.functions.process_event import UnauthorizedAction, process_event
from andreas.functions.verifying import sign_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.signature import UnverifiedSignature
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class TestCreatePost(AndreasTestCaseWithKeyPair):
    """
    Create a simple post by a single event.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
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
        post: Post = Post.select().join(Server).where(Server.name == 'aaa', Post.path == '/post1').get()
        self.assertEqual(self.event.diff, post.data)

class TestModifyPost(AndreasTestCaseWithKeyPair):
    """
    With a pre-existing post, try to create/modify/remove three different fields in ``data``.
    Check that each field was processed correctly and that the fourth field wasn't affected.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
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
    """
    Make sure that processing event will fail with an exception if the signature is corrupted.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'This event should be rejected.',
        }
        self.event.signatures = {
            'abraham@aaa': sign_post(self.event, self.abraham_keypair).hex().replace('a', 'b'),
        }
        self.event.save()
    
    def test_all(self):
        with self.assertRaisesRegex(UnauthorizedAction, 'Missing authorization by abraham@aaa.'):
            process_event(self.event)

class TestPartiallyIncorrectSignature(AndreasTestCaseWithKeyPair):
    """
    Similar to :class:`TestIncorrectSignature` except the event has two signatures and only one is corrupted.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'A normal post.',
        }
        self.event.signatures = {
            'abraham@aaa': sign_post(self.event, self.abraham_keypair).hex(),
            'bernard@aaa': sign_post(self.event, self.bernard_keypair).hex().replace('a', 'b'),
        }
        self.event.save()
        
        process_event(self.event)
    
    def test_post_created(self):
        post: Post = Post.select().join(Server).where(Server.name == 'aaa', Post.path == '/post1').get()
        
        with self.subTest(what='post content'):
            self.assertEqual(self.event.diff, post.data)
        
        with self.subTest(what='unverified signature'):
            us_list = list(UnverifiedSignature.select().where(UnverifiedSignature.post == post))
            self.assertEqual(len(us_list), 1)
            us = us_list[0]
            
            with self.subTest(field='event'):
                self.assertEqual(us.event_id, self.event.id)
            with self.subTest(field='user'):
                self.assertEqual(us.user, 'bernard@aaa')
            with self.subTest(field='data'):
                self.assertEqual(us.data.hex(), self.event.signatures['bernard@aaa'])

class TestUnauthorizedAction(AndreasTestCaseWithKeyPair):
    """
    Make sure that you can't post an Abraham's post with Bernard's signature.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
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

class TestRevalidateWithNewKey(AndreasTestCaseWithKeyPair):
    """
    Create an event which is invalid at first but becomes valid after a new keypair appears.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham@aaa'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'Some text here.',
        }
        self.event.signatures = {
            'abraham@aaa': sign_post(self.event, self.get_abraham2()).hex(),
        }
        self.event.save()
    
    def test_all(self):
        with self.subTest(step='Event is not valid yet'):
            with self.assertRaises(UnauthorizedAction):
                process_event(self.event)
        
        with self.subTest(step='Post is not created'):
            with self.assertRaises(Post.DoesNotExist):
                Post.select().join(Server).where(Server.name == 'aaa', Post.path == '/post1').get()
        
        with self.subTest(step='Event becomes valid'):
            self.load_abraham2()
            process_event(self.event)
        
        with self.subTest(step='Post is created'):
            post: Post = Post.select().join(Server).where(Server.name == 'aaa', Post.path == '/post1').get()
            self.assertEqual(self.event.diff, post.data)