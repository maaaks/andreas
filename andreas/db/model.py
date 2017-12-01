from typing import Dict, List, Optional, Tuple, Type

from playhouse import signals

from andreas.db.database import db


class Model(signals.Model):
    class Meta:
        database = db
        schema = 'andreas'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._models_to_save_after_myself: List[Tuple[Model,Dict]] = []
    
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
                trigger_name = when.replace(' ', '_')
                code = code.rstrip('; \t\n\t')
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
    
    def save_after(self, dependency: 'Model', **kwargs) -> None:
        """
        Registers handler that will automatically save this model right as soon as `dependency` will be saved.
        This handler works only once and unregisters itself after finishing its work.
        """
        dependency._models_to_save_after_myself.append((self, kwargs))
    
    @classmethod
    def create_after(cls, dependency: 'Model', **kwargs) -> 'Model':
        """
        Creates instance and registers handler that will automatically save it as soon as `dependency` will be saved.
        This handler works only once and unregisters itself after finishing its work.
        """
        instance = cls(**kwargs)
        dependency._models_to_save_after_myself.append((instance, {}))
        return instance


@signals.post_save()
def post_save(model_class: Type[Model], instance: Model, created: bool):
    """
    After an object is saved, all other models that waited for it will be automatically saved, too.
    """
    for model, kwargs in instance._models_to_save_after_myself:
        model.save(**kwargs)
    instance._models_to_save_after_myself = []