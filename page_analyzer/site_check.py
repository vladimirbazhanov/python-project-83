import psycopg
import os
from datetime import datetime


class SiteCheck:

    def __init__(self):
        pass

    def save(self):
        created_at = datetime.now()

        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO url_checks (created_at) VALUES (%s)
                    """, (created_at, ))
                conn.commit()