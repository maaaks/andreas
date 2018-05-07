from math import ceil

import psycopg2
from peewee import BlobField


class BlobIntegerField(BlobField):
    """
    Stores a big integer in form of big-endian byte array.
    """
    db_field = 'bytea'
    
    def db_value(self, value: int):
        length = int(ceil(value.bit_length() / 8))
        value_bytes = value.to_bytes(length, 'big')
        return psycopg2.Binary(value_bytes)
    
    def python_value(self, value: bytes) -> int:
        return int.from_bytes(value, 'big')