import validators
import psycopg
import os
from datetime import datetime
from urllib.parse import urlparse


class Site:
    def __init__(self, url):
        self.url = url

    def is_valid(self):
        return validators.url(self.url)


    def save(self):
        url = self.normalized_url()
        created_at = datetime.now()

        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO urls (name, created_at) VALUES (%s, %s)
                    """, (url, created_at))
                conn.commit()

    def normalized_url(self):
        parsed_url = urlparse(self.url)
        return '://'.join([parsed_url.scheme, parsed_url.netloc])