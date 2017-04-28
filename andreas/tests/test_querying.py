from unittest.case import TestCase

from andreas.functions.querying import query_post, query_posts
from andreas.models.core import Post, Server


class TestQuerying(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_a: Server = Server.create(hostname='A')
        Post.create(server=cls.server_a, path='1', data={'body': 'Server A, Post #1'})
        Post.create(server=cls.server_a, path='2', data={'body': 'Server A, Post #2'})
        
        cls.server_b: Server = Server.create(hostname='B')
        Post.create(server=cls.server_b, path='1', data={'body': 'Server B, Post #1'})
        Post.create(server=cls.server_b, path='2', data={'body': 'Server B, Post #2'})
    
    def test_existing_posts(self):
        for server in (self.server_a, self.server_b):
            for path in ('1', '2'):
                with self.subTest(server=server.hostname, path=path):
                    query = '=' + path
                    posts = list(query_posts(server, query))
                    self.assertEqual(len(posts), 1)
                    
                    expected_body = 'Server {}, Post #{}'.format(server.hostname, path)
                    self.assertEqual(posts[0].data['body'], expected_body)
    
    def test_non_existing_post_single(self):
        self.assertIsNone(query_post(self.server_a, '=3'))
    
    def test_non_existing_post_as_list(self):
        self.assertEqual(len(list(query_posts(self.server_a, '=3'))), 0)