import pdb
import os

from flask import Flask, request, flash, redirect, render_template
from dotenv import load_dotenv
import psycopg

from page_analyzer.site import Site
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def get_index():
    return render_template('index.html')


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
    else:
        site = Site(url)
        if not site.is_valid():
            flash('Адрес сайта некорректен, введите снова!', 'warning')
            return redirect('/')
        else:
            try:
                site.save()
            except psycopg.errors.UniqueViolation:
                flash('Сайт уже есть в базе данных!', 'warning')
                return redirect('/')
            finally:
                flash('Сайт успешно добавлен!', 'info')

        return render_template('index.html')

