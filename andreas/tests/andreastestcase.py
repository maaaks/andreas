from os.path import dirname
from unittest.case import TestCase

from peewee import _transaction

from andreas.db.database import db
from andreas.models.keypair import KeyPair
from andreas.models.server import Server
from andreas.models.user import User


class AndreasTestCase(TestCase):
    """
    Basic class for all test cases.
    Begins a database transaction before executing and always rollbacks it after the test is finished.
    """
    @classmethod
    def __init_subclass__(cls, **kwargs):
        if 'setUp' in cls.__dict__:
            raise Exception('Overriding setUp() is forbidden, please override setUpSafe() instead.')
        if 'tearDown' in cls.__dict__:
            raise Exception('Overriding tearDown() is forbidden.')
    
    def setUp(self):
        """
        Creates a transaction and calls :meth:`setUpSafe()` inside it.
        Unlike vanilla ``TestCase``, calls :meth:`tearDown()` if setup fails.
        """
        self.transaction_context = db.atomic()
        self.transaction: _transaction = self.transaction_context.__enter__()
        
        try:
            self.setUpSafe()
        except Exception as e:
            self.tearDown()
            raise e
    
    def setUpSafe(self):
        pass
    
    def tearDown(self):
        self.transaction.rollback(begin=False)
        self.transaction_context.__exit__(None, None, None)


class AndreasTestCaseWithKeyPair(AndreasTestCase):
    """
    Convenient basic class for test cases that need to work with users who have added valid keypairs.
    """
    def setUpSafe(self):
        super().setUpSafe()
        
        self.server: Server = Server.create(name='aaa')
        
        self.abraham: User = User.create(server=self.server, name='abraham')
        self.abraham_keypair = KeyPair.from_file(dirname(__file__) + '/keypairs/abraham.txt', user=self.abraham)
        
        self.bernard: User = User.create(server=self.server, name='bernard')
        self.bernard_keypair = KeyPair.from_file(dirname(__file__) + '/keypairs/bernard.txt', user=self.bernard)
    
    @staticmethod
    def get_abraham2() -> KeyPair:
        """Loads Abraham's second key, returns it but does not save it."""
        return KeyPair.from_file(dirname(__file__) + '/keypairs/abraham-2.txt')
    
    def load_abraham2(self):
        """Loads Abraham's second key, saves it and stores as :data:`abraham_keypair`."""
        self.abraham_keypair = KeyPair.from_file(dirname(__file__) + '/keypairs/abraham-2.txt', user=self.abraham)