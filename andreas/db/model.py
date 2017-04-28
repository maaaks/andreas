from typing import Dict, Optional

import peewee

from andreas.db.database import db


class Model(peewee.Model):
    class Meta:
        database = db
        schema = "andreas"
    
    @classmethod
    def table(cls) -> str:
        return f'{cls._meta.schema}.{cls._meta.db_table}'
    
    @classmethod
    def triggers(cls) -> Optional[Dict[str,str]]:
        return None
    
    @classmethod
    def create_table(cls, fail_silently=False):
        """
        Creates a table for given model and creates/recreates all the triggers on it.
        """
        super().create_table(fail_silently=fail_silently)
        
        if cls.triggers():
            # Remove the old triggers
            for event in 'insert', 'update', 'delete', 'truncate':
                for when in 'before', 'after', 'instead_of':
                    db.execute_sql(f'drop trigger if exists {when}_{event} on {cls.table()}')
                    db.execute_sql(f'drop function if exists on_{cls.table()}_{when}_{event}()')
            
            # Create new triggers
            for when, code in cls.triggers().items():
                trigger_name = when.replace(" ", "_")
                code = code.rstrip("; \t\n\t")
                db.execute_sql(
                    f'create or replace function {cls.table()}_{trigger_name}() returns trigger '
                    f'as $$ begin {code}; end $$ language plpgsql')
                db.execute_sql(
                    f'create trigger {trigger_name} {when} on {cls.table()} '
                    f'for each row execute procedure {cls.table()}_{trigger_name}()')
    
    def reload(self):
        """
        Updates all the fields from the database.
        """
        newer_self = self.get(self._meta.primary_key == self._get_pk_value())
        for field_name in self._meta.fields.keys():
            val = getattr(newer_self, field_name)
            setattr(self, field_name, val)
        self._dirty.clear()