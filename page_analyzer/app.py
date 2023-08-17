import os
import psycopg2
from flask import Flask, request, flash, redirect, render_template
from dotenv import load_dotenv

from page_analyzer.url import Url
from page_analyzer.check import Check

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def get_index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    urls = Url.all()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<url_id>')
def get_url(url_id):
    url = Url.find(url_id)
    checks = url.get_checks()

    return render_template('url.html', url=url, checks=checks)


@app.post('/urls/<url_id>/checks')
def post_checks(url_id):
    url = Url.find(url_id)

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

    url = Url({'name': name})
    if not url.is_valid():
        flash('Адрес сайта некорректен, введите снова!', 'warning')
        return render_template('index.html'), 422

    try:
        url.save()

    except psycopg2.Error:
        flash('Страница уже существует', 'warning')
        return redirect('/')

    flash('Страница успешно добавлена', 'info')
    return redirect(f'/urls/{url.id}')
