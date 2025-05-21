import psycopg2
from .config import Config

class Connection:
    _instance = None
    
    @classmethod
    def getInstance(cls, config=None):
        if cls._instance is None:
            cls._instance = psycopg2.connect(
                host=config.host,
                database=config.database,
                user=config.user,
                password=config.password,
                port=config.port
            )
        return cls._instance

    @classmethod
    def delete_instance(cls):
        cls._instance = None
