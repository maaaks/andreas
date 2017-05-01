from andreas.models.server import Server
from andreas.models.user import User
from andreas.tests.andreastestcase import AndreasTestCase


class TestUser(AndreasTestCase):
    def setUp(self):
        super().setUp()
        
        self.server_a: Server = Server.create(name='aaa')
        self.server_b: Server = Server.create(name='bbb')
        
        self.user_a1: User = User.create(server=self.server_a, name='user1')
        self.user_a2: User = User.create(server=self.server_a, name='user2')
        self.user_b1: User = User.create(server=self.server_b, name='user1')
        self.user_b2: User = User.create(server=self.server_b, name='user2')
        self.user_b3: User = User.create(server=self.server_b, name='user3')
    
    def test_user_a1(self):
        self.assertEqual(User.from_string('user1@aaa').id, self.user_a1.id)
    
    def test_user_a2(self):
        self.assertEqual(User.from_string('user2@aaa').id, self.user_a2.id)
    
    def test_user_b1(self):
        self.assertEqual(User.from_string('user1@bbb').id, self.user_b1.id)
    
    def test_user_b2(self):
        self.assertEqual(User.from_string('user2@bbb').id, self.user_b2.id)
    
    def test_user_b3(self):
        self.assertEqual(User.from_string('user3@bbb').id, self.user_b3.id)
    
    def test_non_existent_user(self):
        with self.assertRaises(User.DoesNotExist):
            User.from_string('user3@aaa')
    
    def test_create_user(self):
        self.assertIsNotNone(User.from_string('user3@aaa', create=True))