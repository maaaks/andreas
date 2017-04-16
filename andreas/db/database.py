from typing import List

import peewee
from playhouse.postgres_ext import PostgresqlExtDatabase

from andreas.app import app


class Database(PostgresqlExtDatabase):
    def __init__(self, **kwargs):
        kwargs["register_hstore"] = False
        super().__init__(app.config.db.database, host=app.config.db.host, port=app.config.db.port,
            user=app.config.db.user, password=app.config.db.password, **kwargs)
    
    def create_tables(self, models: List[peewee.Model], safe: bool = False):
        for schema in set(m._meta.schema for m in models):
            self.execute_sql(f'create schema if not exists {schema}')
        super().create_tables(models, safe)
    
    def create_table(self, model_class: peewee.Model, safe: bool = False):
        self.execute_sql(f'create schema if not exists {model_class._meta.schema}')
        super().create_table(model_class, safe)


db = Database()