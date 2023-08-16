import pdb

import validators
import psycopg
import os
from datetime import datetime
from urllib.parse import urlparse
from page_analyzer.check import Check


class Url:
    def __init__(self, id=None, name='', created_at=datetime.now()):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.normalized_url = '://'.join(
            [urlparse(self.name).scheme, urlparse(self.name).netloc]
        )


    @staticmethod
    def all():
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, created_at
                    FROM urls
                    ORDER BY created_at DESC
                    """
                )
                results = cur.fetchall()
                urls = list(map(Url.build, results))
        return urls

    @ staticmethod
    def build(params):
        return Url(id=params[0], name=params[1], created_at=str(params[2]))

    @staticmethod
    def find(id):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, created_at FROM urls WHERE id = %s
                    """, (id, )
                )
                result = cur.fetchone()
        return Url.build(result)


    def get_checks(self):
        return Check.find_by_url_id(url_id)


    def is_valid(self):
        return (validators.url(self.url)
                and validators.length(self.url, max=255))

    def save(self):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO urls (name, created_at) VALUES (%s, %s)
                    """, (self.normalized_url, self.created_at, ))
                conn.commit()
