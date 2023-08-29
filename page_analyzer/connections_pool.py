import os
from psycopg2 import pool


class ConnectionsPool:
    def __init__(self):
        self.pool = pool.SimpleConnectionPool(1, 5, os.environ['DATABASE_URL'])

    def __enter__(self):
        self.connection = self.pool.getconn()

        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.putconn(self.connection)
        self.connection = None
