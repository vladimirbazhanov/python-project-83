import requests
from datetime import datetime
from bs4 import BeautifulSoup
import page_analyzer.app as app


class Check:
    def __init__(self, params):
        self.id = params.get('id')
        self.status_code = params.get('status_code')
        self.title = params.get('title')
        self.h1 = params.get('h1')
        self.description = params.get('description')
        self.created_at = params.get('created_at', datetime.now())

        self.url = params.get('url')
        self.errors = []

    @staticmethod
    def build(params):
        return Check(
            {
                'id': params[0],
                'status_code': params[1],
                'title': params[2],
                'h1': params[3],
                'description': params[4],
                'created_at': params[5]
            }
        )

    @staticmethod
    def find_by_url_id(url_id):
        with app.connections_pool as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, status_code, title, h1, description, created_at
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
                self.__parse_response(response)
                self.save()
            else:
                self.errors.append('Произошла ошибка при проверке')

        except Exception as ex:
            self.errors.append(str(ex))

    def save(self):
        with app.connections_pool as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        INSERT INTO
                        url_checks (
                          url_id,
                          status_code,
                          title,
                          h1,
                          description,
                          created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        self.url.id,
                        self.status_code,
                        self.title,
                        self.h1,
                        self.description,
                        self.created_at,)
                )
                conn.commit()

    def __parse_response(self, response):
        soup = BeautifulSoup(response.text)

        self.title = soup.title.text if soup.title else 'Не найден'
        self.h1 = soup.h1.text if soup.h1 else 'Не найден'
        self.status_code = response.status_code

        meta = soup.find('meta', {'name': 'description'})
        self.description = meta.attrs['content'] if meta else 'Не найден'
