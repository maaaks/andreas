from typing import Iterable

from andreas.functions.querying import get_post
from andreas.models.core import Post, Server
from andreas.tests.testcase import AndreasTestCase


class TestQuerying(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.server_a: Server = Server.create(hostname='A')
        self.server_b: Server = Server.create(hostname='B')
        
        self.posts: Iterable[Post] = (
            Post.create(server=self.server_a, path='/post1', data={'body': 'Server A, Post #1'}),
            Post.create(server=self.server_a, path='/post2', data={'body': 'Server A, Post #2'}),
            Post.create(server=self.server_b, path='/post1', data={'body': 'Server B, Post #1'}),
            Post.create(server=self.server_b, path='/post2', data={'body': 'Server B, Post #2'}),
        )
    
    def test_existing_posts(self):
        for post in self.posts:
            for server in (post.server, post.server.id, post.server.hostname):
                with self.subTest(
                    server=post.server.hostname,
                    server_param_type=type(server).__name__,
                    path=post.path
                ):
                    self.assertEqual(post.data['body'], get_post(server, post.path).data['body'])
    
    def test_non_existing_post(self):
        for server in (self.server_a, self.server_a.id, self.server_a.hostname):
            with self.subTest(server_param_type=type(server).__name__):
                with self.assertRaises(Post.DoesNotExist):
                    get_post(self.server_a, '3')