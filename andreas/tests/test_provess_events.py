from unittest.case import TestCase

from andreas.functions.process_events import process_event
from andreas.models.core import Event, Post, Server


class TestCreatePost(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event = Event()
        cls.event.hostname = 'localhost'
        cls.event.path = '/post1'
        cls.event.diff = {
            'body': 'Hello, World!',
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        cls.event.hashes = {
            '=/post1': ['sha256', '5c56d4fea85167a48b7f71be87b855bd8dacf0c75ba2457fc9b007ae61be05c9'],
        }
        cls.event.save()
        process_event(cls.event)
    
    def test_all(self):
        post: Post = (Post.select()
            .join(Server)
            .where(Server.hostname == 'localhost')
            .where(Post.path == '/post1')
            .get())
        self.assertEqual(self.event.diff, post.data)

class TestModifyPost(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post = Post()
        cls.post.server = Server.local()
        cls.post.path = '/post2'
        cls.post.data = {
            'title': 'Hello',
            'subtitle': 'A hello world post',
            'body': 'Hello, World!',
        }
        cls.post.save()
        
        event = Event()
        event.hostname = 'localhost'
        event.path = '/post2'
        event.diff = {
            'title': 'Hello (updated)',
            'subtitle': None,
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        event.hashes = {
            '=/post2': ['sha256', '915002cf719e1c0cfdc1783615217370dda8b3ec445cb4a48701a6384f859cc2'],
        }
        event.save()
        process_event(event)
        
        cls.post.reload()
    
    def test_title_updated(self):
        self.assertEqual('Hello (updated)', self.post.data['title'])
    
    def test_subtitle_removed(self):
        self.assertFalse('subtitle' in self.post.data)
    
    def test_body_untouched(self):
        self.assertEqual('Hello, World!', self.post.data['body'])
    
    def test_tags_added(self):
        self.assertEqual(['Aaa', 'Bbb', 'Ccc'], self.post.data['tags'])