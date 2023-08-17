import pdb

import psycopg
import os
import requests
from datetime import datetime


class Check:
    def __init__(self, params):
        self.id = params.get('id')
        self.status_code = params.get('status_code')
        self.created_at = params.get('created_at', datetime.now())

        self.url = params.get('url')

        self.errors = []


    @staticmethod
    def build(params):
        return Check({'id': params[0], 'status_code': params[1], 'created_at': params[2]})


    @staticmethod
    def find_by_url_id(url_id):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, status_code, created_at
                    FROM url_checks
                    WHERE url_id = %s
                    """, (url_id, )
                )
                results = cur.fetchall()
                checks = list(map(Check.build, results))
        return checks


    def perform(self):
        try:
            response = requests.get(self.url.name)

            if response.status_code == 200:
                self.status_code = response.status_code
                self.save()
            else:
                self.errors.append('Произошла ошибка при проверке')

        except Exception as ex:
            self.errors.append(str(ex))

    def save(self):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO url_checks (url_id, status_code, created_at)
                        VALUES (%s, %s, %s)
                    """, (self.url.id, self.status_code, self.created_at, ))
                conn.commit()
