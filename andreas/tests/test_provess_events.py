from andreas.functions.process_events import IncorrectEventHashes, process_event
from andreas.functions.querying import get_post
from andreas.models.core import Event, Post, Server
from andreas.tests.testcase import AndreasTestCase


class TestCreatePost(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.hostname = 'localhost'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'Hello, World!',
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        self.event.hashes = {
            'md5': '06cbcd41977eb05c931fe10ac1664fab',
            'sha1': 'd25ef9e95ae7f5698e7e6dc1c656e0e88a708dc2',
            'sha256': '5c56d4fea85167a48b7f71be87b855bd8dacf0c75ba2457fc9b007ae61be05c9',
            'sha512': '3b589982b83bbc471968bdf30a149462a48350453017a03fc9a8a593cfa127abec7b1508f106bb97b16af6c54e1da1e5f21a364fbf87cd189039b9d99cebb42b',
        }
        self.event.save()
        process_event(self.event)
    
    def test_all(self):
        post: Post = (Post.select()
            .join(Server)
            .where(Server.hostname == 'localhost')
            .where(Post.path == '/post1')
            .get())
        self.assertEqual(self.event.diff, post.data)

class TestModifyPost(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.post = Post()
        self.post.server = Server.local()
        self.post.path = '/post1'
        self.post.data = {
            'title': 'Hello',
            'subtitle': 'A hello world post',
            'body': 'Hello, World!',
        }
        self.post.save()
        
        event = Event()
        event.hostname = 'localhost'
        event.path = '/post1'
        event.diff = {
            'title': 'Hello (updated)',
            'subtitle': None,
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        event.hashes = {
            'md5': '099746143cdb545dd2778393b86a7e24',
            'sha1': '2ce9e727a1ccc16de3d44e1b03570c412e7c0ed3',
            'sha256': '915002cf719e1c0cfdc1783615217370dda8b3ec445cb4a48701a6384f859cc2',
            'sha512': 'cbde8c14c26256855b59d26398a9b0e25b77f6fd2a29d9bf317b789700c1d15170a0faadcfa80defb32af6c204a784dd03baef088a7b687f690459cecf80f244',
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

class TestIncorrectHashes(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.server: Server = Server.create(hostname='A')
        
        self.event = Event()
        self.event.hostname = 'A'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'This event should be rejected.',
        }
        self.event.hashes = {
            'sha256': 'b267a9d77b86a57125b2ac6939951582e2a0e24a775fcbac8c26a791f8d6a490',
        }
        self.event.save()
    
    def test_all(self):
        with self.assertRaisesRegex(IncorrectEventHashes, 'Incorrect hash for sha256.'):
            process_event(self.event)
        
        # After an invalid event, post is not being created
        with self.assertRaises(Post.DoesNotExist):
            get_post(self.server, '/post1')