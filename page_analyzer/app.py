import pdb
import os

from flask import Flask, request, flash, redirect, render_template
from dotenv import load_dotenv
import psycopg

from page_analyzer.site import Site
from page_analyzer.site_check import SiteCheck

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def get_index():
    return render_template('index.html')


@app.route('/urls/<id>')
def get_url(id):
    url = Site.find(id)

    return render_template('url.html', url=url)


@app.post('/urls/<url_id>/checks')
def post_checks(url_id):
    url = Site.find(url_id)

    site_check = SiteCheck()
    site_check.save()

    return redirect(f'/urls/{url[0]}')


@app.get('/urls')
def get_urls():
    urls = Site.all()

    return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    if not url:
        flash('Пожалуйста, введите адрес сайта!', 'warning')
        return redirect('/')

    site = Site(url)
    if not site.is_valid():
        flash('Адрес сайта некорректен, введите снова!', 'warning')
        return redirect('/')

    try:
        site.save()
    except psycopg.errors.UniqueViolation:
        flash('Сайт уже есть в базе данных!', 'warning')
        return redirect('/')

    flash('Сайт успешно добавлен!', 'info')
    return render_template('index.html')

