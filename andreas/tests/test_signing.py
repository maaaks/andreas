import json

import rsa

from andreas.functions.verifying import sign_post, verify_post
from andreas.models.event import Event
from andreas.models.post import Post
from andreas.models.relations import UserPostRelation
from andreas.tests.andreastestcase import AndreasTestCaseWithKeyPair


class _TestSigning(AndreasTestCaseWithKeyPair):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.expected = rsa.sign(
            json.dumps({
                'server': 'aaa',
                'path': '/post1',
                'authors': ['abraham@aaa'],
                'data': {'foo': 'bar', 'bar': 'baz'},
            }, sort_keys=True).encode(),
            self.abraham_keypair.privkey,
            'SHA-512')


class TestSigningPost(_TestSigning):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.post = Post()
        self.post.server = self.server
        self.post.path = '/post1'
        self.post.data = {'foo': 'bar', 'bar': 'baz'}
        self.post.save()
        
        UserPostRelation.create(source=self.abraham, type='wrote', target=self.post)
    
    def test_sign(self):
        self.assertEqual(sign_post(self.post, self.abraham_keypair), self.expected)
    
    def test_verify(self):
        verify_post(self.post, 'abraham@aaa', self.expected)


class TestSigningEvent(_TestSigning):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.event = Event()
        self.event.authors = ['abraham@aaa']
        self.event.server = 'aaa'
        self.event.path = '/post1'
        self.event.diff = {'foo': 'bar', 'bar': 'baz'}
        self.event.save()
    
    def test_sign(self):
        self.assertEqual(sign_post(self.event, self.abraham_keypair), self.expected)
    
    def test_verify(self):
        verify_post(self.event, 'abraham@aaa', self.expected)


class TestSigningEventWithCustomData(_TestSigning):
    def setUpSafe(self):
        super().setUpSafe()
        
        self.event = Event()
        self.event.authors = ['abraham@aaa']
        self.event.server = 'aaa'
        self.event.path = '/post1'
        self.event.diff = {'foo': 'bar'}
        self.event.save()
    
    def test_sign(self):
        self.assertEqual(sign_post(self.event, self.abraham_keypair, data={'foo': 'bar', 'bar': 'baz'}), self.expected)
    
    def test_verify(self):
        verify_post(self.event, 'abraham@aaa', self.expected, data={'foo': 'bar', 'bar': 'baz'})