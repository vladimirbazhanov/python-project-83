import psycopg
import os
from datetime import datetime


class SiteCheck:

    def __init__(self, url_id):
        self.url_id = url_id
        pass

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
                result = cur.fetchall()

        return result

    def save(self):
        created_at = datetime.now()

        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO url_checks (url_id, created_at)
                        VALUES (%s, %s)
                    """, (self.url_id, created_at, ))
                conn.commit()
