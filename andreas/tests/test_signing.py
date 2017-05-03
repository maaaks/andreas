from andreas.functions.verifying import sign_post, verify_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class TestSigning(AndreasTestCaseWithKeyPair):
    """
    This test checks correct work
    of :func:`sign_post()<andreas.functions.verifying.sign_post>`
    and :func:`verify_post()<andreas.functions.verifying.verify_post>`.
    """
    expected = bytes.fromhex(
        '249e9e65ad432534891fce422436d892901ee2b7d9bf38686e5c4976c771f82a'
        'ab49918c48191cd8cbbb3378ee4aad21f9f99f914ed837809601454fa576668b'
        '31b29a33bd32c85044a6ab6dde4d4a29203bf0519ccf800d6ecc647b494b8eb7'
        'c2e7693c581604e84e459bfb1aeba91ba7ae5ff66678cc54671c2131f46d5c46'
        'c2a9b6cab9bdfcb0c4bed18da6651a7f3e14b12853ed4acb9e5965b0fd566f22'
        '8faae7713ff1caa62ef9ce34ce54ac7622fe4e5c01b4142cf071188e5f3622d0'
        'a0c7865b19cd4c17b3e1750a9398c26d2f4c4d59943744e97e0b043399700cf2'
        '6b29eda2c09930f0f57831de775684c07f08fdb2542ea4ca7f203788f018743c'
    )
    
    def setUp(self):
        super().setUp()
        
        # A simple post
        self.post1 = Post()
        self.post1.user = self.abraham
        self.post1.server = self.server
        self.post1.path = '/post1'
        self.post1.data = {'foo':'bar', 'bar':'baz'}
        
        # An event with the same content
        self.event1 = Event()
        self.event1.user = 'abraham@aaa'
        self.event1.server = 'aaa'
        self.event1.path = '/post1'
        self.event1.diff = {'foo':'bar', 'bar':'baz'}
        
        # Another event, with less data in it
        self.event2 = Event()
        self.event2.user = 'abraham@aaa'
        self.event2.server = 'aaa'
        self.event2.path = '/post1'
        self.event2.diff = {'foo':'bar'}
    
    def test_sign(self):
        with self.subTest(what='post1'):
            self.assertEqual(sign_post(self.post1, self.abraham_keypair), self.expected)
        
        with self.subTest(what='event1'):
            self.assertEqual(sign_post(self.event1, self.abraham_keypair), self.expected)
        
        with self.subTest(what='event2'):
            self.assertEqual(sign_post(self.event2, self.abraham_keypair, data={'foo':'bar', 'bar':'baz'}),
                self.expected)
    
    def test_verify(self):
        with self.subTest(what='post1'):
            verify_post(self.post1, 'abraham@aaa', self.expected)
        
        with self.subTest(what='event1'):
            verify_post(self.event1, 'abraham@aaa', self.expected)
        
        with self.subTest(what='event2'):
            verify_post(self.event2, 'abraham@aaa', self.expected, data={'foo':'bar', 'bar':'baz'})