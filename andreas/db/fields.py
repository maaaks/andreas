from math import ceil

from peewee import BlobField, SQL


class BlobIntegerField(BlobField):
    """
    Stores a big integer in form of big-endian byte array.
    """
    db_field = 'bytea'
    
    def db_value(self, value: int):
        length = int(ceil(value.bit_length() / 8))
        hex_value = value.to_bytes(length, 'big').hex()
        return SQL(fr"E'\\x{hex_value}'")
    
    def python_value(self, value: bytes) -> int:
        return int.from_bytes(value, 'big')