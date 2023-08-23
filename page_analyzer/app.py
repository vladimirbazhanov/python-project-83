import os

from psycopg2 import pool
from flask import Flask, request, flash, redirect, render_template
from dotenv import load_dotenv
from page_analyzer.url import Url
from page_analyzer.check import Check

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

connections_pool = pool.SimpleConnectionPool(
    1, 5, os.environ['DATABASE_URL']
)
connection = connections_pool.getconn()


@app.route('/')
def get_index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    urls = Url.all()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<url_id>')
def get_url(url_id):
    url = Url.find_by_id(url_id)
    if url:
        checks = url.get_checks()
        return render_template('url.html', url=url, checks=checks)
    else:
        flash('Страница не существует', 'info')
        return redirect('/')


@app.post('/urls/<url_id>/checks')
def post_checks(url_id):
    url = Url.find_by_id(url_id)

    check = Check({'url': url})
    check.perform()

    if check.errors:
        flash(', '.join(check.errors), 'warning')
    else:
        flash('Страница успешно проверена', 'info')
    return redirect(f'/urls/{url.id}')


@app.post('/urls')
def post_urls():
    name = request.form.get('url')
    if not name:
        flash('Пожалуйста, введите адрес сайта!', 'warning')
        return redirect('/')

    url = Url.find_by_name(name)
    if url:
        flash('Страница уже существует', 'info')
        return redirect(f'/urls/{url.id}')
    else:
        url = Url({'name': name})

    if not url.is_valid():
        flash('Некорректный URL', 'warning')
        return render_template('index.html'), 422

    url.save()

    if url.errors:
        flash(', '.join(url.errors), 'warning')
        return redirect('/urls')
    else:
        flash('Страница успешно добавлена', 'info')
        return redirect(f'/urls/{url.id}')
