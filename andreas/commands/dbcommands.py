from typing import List, Type

from andreas.core.entry import Entry
from andreas.core.links import Link_EntryToEntry, Link_EntryToUser, Link_UserToEntry
from andreas.core.server import Server
from andreas.core.user import User
from andreas.db.database import db
from andreas.db.model import Model

models: List[Type[Model]] = [
    Entry,
    Link_EntryToEntry,
    Link_EntryToUser,
    Link_UserToEntry,
    Server,
    User,
]

@db.atomic()
def updatedb():
    db.create_tables(models, safe=True)

@db.atomic()
def populatedb():
    updatedb()
    
    # Local server
    if not Server.select().where(Server.is_local).count():
        server = Server()
        server.is_local = True
        server.hostname = 'localhost'
        server.engine_name = 'Andreas'
        server.engine_version = '0.0.1'
        server.save()
    
    # Local user
    if not User.select().count():
        user = User()
        user.server = Server.get(Server.is_local)
        user.login = 'root'
        user.save()

@db.atomic()
def dropdb():
    db.drop_tables(models, safe=True)

@db.atomic()
def resetdb():
    dropdb()
    populatedb()