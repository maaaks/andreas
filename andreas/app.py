from flask import Config
from flask.app import Flask


class AndreasConfig(Config):
    class db:
        host: str = 'localhost'
        port: int = 5432
        user: str
        password: str
        database: str


class AndreasApp(Flask):
    config_class = AndreasConfig
    config: AndreasConfig


app = AndreasApp('AndreasApp')


try:
    import local_config
except ImportError:
    print("Can't load local_config.py")
    pass