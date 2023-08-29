import validators
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
import page_analyzer.app as app
from page_analyzer.check import Check


class Url:
    def __init__(self, params):
        self.id = params.get('id')
        self.name = params.get('name', '')
        self.created_at = params.get('created_at', datetime.now())
        self.status_code = params.get('status_code')
        self.normalized_url = Url.normalized_url(self.name)
        self.errors = []

    @staticmethod
    def normalized_url(url):
        return '://'.join([urlparse(url).scheme, urlparse(url).netloc])

    @staticmethod
    def all():
        with app.connections_pool as conn:
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
        with app.connections_pool as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, created_at FROM urls WHERE id = %s
                    """, (id, )
                )
                result = cur.fetchone()
        return Url.build(result) if result else None

    def find_by_name(name):
        name = Url.normalized_url(name)
        with app.connections_pool as conn:
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
            with app.connections_pool as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                            INSERT INTO urls (name, created_at)
                            VALUES (%s, %s)
                            RETURNING id
                        """,
                        (Url.normalized_url(self.name), self.created_at, ))
                    self.id = cur.fetchone()[0]
                    conn.commit()
        except psycopg2.Error:
            self.errors.append('Страница уже существует')
