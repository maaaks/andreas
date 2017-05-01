from unittest.case import TestCase

from andreas.db.database import db


class AndreasTestCase(TestCase):
    def setUp(self):
        self.transaction = db.transaction()
        self.transaction.__enter__()
    
    def tearDown(self):
        self.transaction.rollback()