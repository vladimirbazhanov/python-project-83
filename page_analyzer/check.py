import psycopg
import os
import requests
from datetime import datetime


class Check:
    def __init__(self, params):
        self.id = params.get('id')
        self.url = params.get('url')
        self.created_at = params.get('created_at', datetime.now())
        self.errors = []


    @staticmethod
    def build(params):
        return Check({'id': params[0], 'created_at': params[1]})


    @staticmethod
    def find_by_url_id(url_id):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, created_at
                    FROM url_checks
                    WHERE url_id = %s
                    """, (url_id, )
                )
                results = cur.fetchall()
                checks = list(map(Check.build, results))
        return checks


    def perform(self):
        response = requests.get(self.url.name)
        self.save()

    def save(self):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO url_checks (url_id, created_at)
                        VALUES (%s, %s)
                    """, (self.url.id, self.created_at, ))
                conn.commit()
