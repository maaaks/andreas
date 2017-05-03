from typing import Iterable

from andreas.functions.querying import get_post
from andreas.models.post import Post
from andreas.models.server import Server
from andreas.models.user import User
from andreas.tests.andreastestcase import AndreasTestCase


class TestQuerying(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.server_a: Server = Server.create(name='A')
        self.server_b: Server = Server.create(name='B')
        
        self.user_a1: User = User.create(server=self.server_a, name='A1')
        self.user_a2: User = User.create(server=self.server_a, name='A2')
        self.user_b1: User = User.create(server=self.server_b, name='B1')
        self.user_b2: User = User.create(server=self.server_b, name='B2')
        
        self.posts: Iterable[Post] = (
            Post.create(server=self.server_a, user=self.user_a1, path='/post1', data={'body': 'Server A, Post #1'}),
            Post.create(server=self.server_a, user=self.user_a1, path='/post2', data={'body': 'Server A, Post #2'}),
            Post.create(server=self.server_a, user=self.user_a2, path='/post3', data={'body': 'Server A, Post #3'}),
            Post.create(server=self.server_a, user=self.user_a2, path='/post4', data={'body': 'Server A, Post #4'}),
            
            Post.create(server=self.server_b, user=self.user_b1, path='/post1', data={'body': 'Server B, Post #1'}),
            Post.create(server=self.server_b, user=self.user_b1, path='/post2', data={'body': 'Server B, Post #2'}),
            Post.create(server=self.server_b, user=self.user_b2, path='/post3', data={'body': 'Server B, Post #3'}),
            Post.create(server=self.server_b, user=self.user_b2, path='/post4', data={'body': 'Server B, Post #4'}),
        )
    
    def test_existing_posts(self):
        for post in self.posts:
            for server in (post.server, post.server.id, post.server.name):
                with self.subTest(
                    server=post.server.name,
                    server_param_type=type(server).__name__,
                    path=post.path
                ):
                    found_post = get_post(server, post.path)
                    self.assertEqual(post.data['body'], found_post.data['body'])
    
    def test_non_existing_post(self):
        for server in (self.server_a, self.server_a.id, self.server_a.name):
            with self.subTest(server_param_type=type(server).__name__):
                with self.assertRaises(Post.DoesNotExist):
                    get_post(self.server_a, '3')