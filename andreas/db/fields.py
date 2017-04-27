from lxml import etree
from peewee import Clause, Field


class XmlField(Field):
    """Peewee field representing an XML element."""
    db_field = 'xml'
    
    def db_value(self, value):
        if value:
            return Clause('xmlparse (content', etree.tostring(value), ')')
    
    def python_value(self, value):
        return etree.fromstring(value)