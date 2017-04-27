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
            'body': 'Hello, World!',
        }
        cls.post.save()
        
        event = Event()
        event.hostname = 'localhost'
        event.path = '/post2'
        event.diff = {
            'tags': ['Aaa', 'Bbb', 'Ccc'],
            'title': None,
        }
        event.save()
        process_event(event)
    
    def test_all(self):
        post: Post = (Post.select()
            .where(Post.server == Server.local())
            .where(Post.path == '/post2')
            .get())
        
        expected = {
            'body': 'Hello, World!',
            'tags': ['Aaa', 'Bbb', 'Ccc'],
        }
        self.assertEqual(expected, post.data)