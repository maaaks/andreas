from datetime import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, PrimaryKeyField, fn

from andreas.db.model import Model
from andreas.models.server import Server


class User(Model):
    id: int = PrimaryKeyField()
    created: datetime = DateTimeField(default=fn.now)
    modified: datetime = DateTimeField(default=fn.now)
    
    server: Server = ForeignKeyField(Server, on_update='cascade')
    """Server where this user is registered."""
    
    name: str = CharField(50)
    """User's identification on its server."""
    
    @classmethod
    def triggers(cls):
        return {
            'before update': 'new.modified = now(); return new;',
        }
    
    @classmethod
    def from_string(cls, identificator: str, *, create: bool = False) -> "User":
        """
        Given a string formatted like ``server/user``, returns the user `user` at the server `server`.
        The first occurence of a slash is the separator.
        
        :param identificator: The full identificator of the user.
        :param create: When `True`, the user and server will be automatically added to database if not exist.
        """
        server_name, user = identificator.split('/', maxsplit=1)
        try:
            return (User.select(User, Server)
                .join(Server)
                .where(Server.name == server_name)
                .where(User.name == user)
                .get())
        except User.DoesNotExist as e:
            if create:
                server, _ = Server.get_or_create(name=server_name)
                return User.create(server=server, name=user)
            else:
                raise e