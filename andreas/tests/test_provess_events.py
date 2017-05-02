from os.path import dirname

from andreas.functions.process_events import CouldNotVerifySignatures, process_event
from andreas.functions.querying import get_post
from andreas.models.event import Event
from andreas.models.keypair import KeyPair
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.user import User
from andreas.tests.andreastestcase import AndreasTestCase


class _TestWithKeyPair(AndreasTestCase):
    """
    Defines user `user1@aaa` that has a keypair.
    This is useful for all tests in this file.
    """
    def setUp(self):
        super().setUp()
        
        self.server: Server = Server.create(name='aaa')
        
        self.abraham: User = User.create(server=self.server, name='abraham')
        KeyPair.from_file(dirname(__file__) + '/keypairs/abraham.txt', user=self.abraham)
        
        self.bernard: User = User.create(server=self.server, name='bernard')
        KeyPair.from_file(dirname(__file__) + '/keypairs/bernard.txt', user=self.bernard)

class TestCreatePost(_TestWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'Hello, World!',
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        self.event.signatures = {
            'abraham@aaa':
                '1ab07274eddcbebcdd9fa50306e4a75bb6ba99dac7129f23bbdbcc9de5737934'
                '1ea150bc12f8cf644d0f75ecaf936fb7b8644aa61bbd09630bd08d013e02dde7'
                '6ff938c7397a5de7859e4467a9c9fa228d291fe35e88a2e3da5878b35e1782e7'
                'a4584510d1a362da75fdf533f7041e2ae2f2e12203851a8456b05f9e22b0ecc4'
                'fc00641672420585dcaa298203371d3b5864637c60cf4a4922553cb92d1de6e4'
                'bf7e6473cf35d8cd23533b0c8cef7db714313afff90f8400025910e3118abaab'
                'b2eed47ffb2f74a1c4f75e5a9da47268ea2abfdf5e4f902919807c97891cf528'
                '913d1a318ff8194c41323cabc2567792ebba73def923692c7384b2ce322b93c7',
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

class TestModifyPost(_TestWithKeyPair):
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
        event.user = 'abraham'
        event.path = '/post1'
        event.diff = {
            'title': 'Hello (updated)',
            'subtitle': None,
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        event.signatures = {
            'abraham@aaa':
                'aeb3d948a5711c43a59101c8ead56824e489f4497d164f42f5798e44030cc510'
                'b476571249bf0f244b3dcd199152d3f1b940969c9f96b3cc72a33305cef43bb0'
                'f47f62bc5538b6d115fb5fb1b13d4129aee055d36f5a3ebadd3e36198f14f012'
                '9c4a7e80da3fbf0e2dd138b7e43eecb55f193a0bbf14eca27baed7836c9e1560'
                'ef048a00e161adb8e2c6602deb9254105b50092f9e8d2dafb41b0bc45c5bb4e8'
                '60af22c083f9cab0ddedad184e427faf4db0c8962a20d777522ac859cb5c8c9a'
                '3a8b76e91fdb0f080dafef63d960c00f48d905d2e95bfd3a4c05ab16c3131003'
                'e11e3d96787342960d631a8a3fcb2a873470fc5d6a7799c639bab82a85d2ac48',
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

class TestIncorrectSignature(_TestWithKeyPair):
    def setUp(self):
        super().setUp()
        
        self.event = Event()
        self.event.server = 'aaa'
        self.event.user = 'abraham'
        self.event.path = '/post1'
        self.event.diff = {
            'body': 'This event should be rejected.',
        }
        self.event.signatures = {
            'abraham@aaa':
                '041958d87fb4c256887ec00d5d6918ea313a60aac67b3a807678c19c95519dfb'
                'bacc08e62d132f8f9764ca8949330c8f70142e7e7750f2675c73a0884898ca98'
                '81f3ada5de61735b8075c879d38a2198cc0f5eb64431b79ee3c1e24b0a84339b'
                '7a00a24a05d5230dd4de19d3eccab02d6458b66cf657ea74d9d8a13f8c1beb4d'
                '1579277da81de11b6280b2dd0da308060e198d128805d007035ddecca63167e6'
                '6fed8a4c858859116ec3ddc112f169fce0aa492705dff22ceffc4d333bcd30a4'
                '32ce6e3999453d684c42daa8fbf0bf1ee068d581319657da4902f7b0f2bf7154'
                '3392c253c1734179917850db3c790f1756c1b4a882f982323d544007076dc548',
        }
        self.event.save()
    
    def test_all(self):
        with self.assertRaises(CouldNotVerifySignatures):
            process_event(self.event)
        
        # After an invalid event, post is not being created
        with self.assertRaises(Post.DoesNotExist):
            get_post(self.server, '/post1')