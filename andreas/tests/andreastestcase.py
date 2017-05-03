from os.path import dirname
from unittest.case import TestCase

from andreas.db.database import db
from andreas.models.keypair import KeyPair
from andreas.models.server import Server
from andreas.models.user import User


class AndreasTestCase(TestCase):
    """
    Basic class for all test cases.
    Begins a database transaction before executing and always rollbacks it after the test is finished.
    """
    def setUp(self):
        self.transaction = db.transaction()
        self.transaction.__enter__()
    
    def tearDown(self):
        self.transaction.rollback()

class AndreasTestCaseWithKeyPair(AndreasTestCase):
    """
    Convenient basic class for test cases that need to work with users who have added valid keypairs.
    """
    def setUp(self):
        super().setUp()
        
        self.server: Server = Server.create(name='aaa')
        
        self.abraham: User = User.create(server=self.server, name='abraham')
        self.abraham_keypair = KeyPair.from_file(dirname(__file__) + '/keypairs/abraham.txt', user=self.abraham)
        
        self.bernard: User = User.create(server=self.server, name='bernard')
        self.bernard_keypair = KeyPair.from_file(dirname(__file__) + '/keypairs/bernard.txt', user=self.bernard)