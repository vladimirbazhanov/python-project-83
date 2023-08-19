import validators
import psycopg2
import os
from datetime import datetime
from urllib.parse import urlparse
from page_analyzer.check import Check


class Url:
    def __init__(self, params):
        self.id = params.get('id')
        self.name = params.get('name', '')
        self.created_at = params.get('created_at', datetime.now())
        self.status_code = params.get('status_code')
        self.normalized_url = '://'.join(
            [urlparse(self.name).scheme, urlparse(self.name).netloc]
        )

        self.errors = []

    @staticmethod
    def all():
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT urls.id,
                           urls.name,
                           MAX(url_checks.created_at),
                           url_checks.status_code
                    FROM url_checks
                    RIGHT JOIN urls ON url_checks.url_id = urls.id
                    GROUP BY urls.id, urls.name, url_checks.status_code;
                    """
                )
                results = cur.fetchall()
                urls = list(map(Url.build, results))
        return urls

    @ staticmethod
    def build(params):
        return Url({
            'id': params[0],
            'name': params[1],
            'created_at': str(params[2]),
            'status_code': params[3] if len(params) == 4 else ''
        })

    @staticmethod
    def find_by_id(id):
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, created_at FROM urls WHERE id = %s
                    """, (id, )
                )
                result = cur.fetchone()
        return Url.build(result)

    def find_by_name(name):
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, created_at FROM urls WHERE name = %s
                    """, (name, )
                )
                result = cur.fetchone()
        return Url.build(result) if result else None

    def get_checks(self):
        return Check.find_by_url_id(self.id)

    def is_valid(self):
        return (validators.url(self.name)
                and validators.length(self.name, max=255))

    def save(self):
        try:
            with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                            INSERT INTO urls (name, created_at)
                            VALUES (%s, %s)
                            RETURNING id
                        """, (self.normalized_url, self.created_at, ))
                    self.id = cur.fetchone()[0]
        except psycopg2.Error:
            self.errors.append('Страница уже существует')
