import asyncio

import aiohttp
from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import UploadForm, URLMapForm
from .models import URLMap
from .utils import get_unique_short_id, process_file


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data

        short = custom_id or get_unique_short_id(URLMap)
        if (
            short == 'files'
            or URLMap.query.filter_by(short=short).first() is not None
        ):
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)

        url_map = URLMap(
            original=original,
            short=short,
        )

        db.session.add(url_map)
        db.session.commit()

        link = url_for('redirect_view', short=short, _external=True)
        flash(
            f'Ваша короткая ссылка: '
            f'<a href="{link}" target="_blank">{link}</a>'
        )
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)


@app.route('/<string:short>')
def redirect_view(short):
    """Перенаправление на оригинальную ссылку."""
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
async def upload_files_view():
    form = UploadForm()
    if form.validate_on_submit():
        async with aiohttp.ClientSession() as session:
            tasks = [
                process_file(session, file)
                for file in form.files.data
            ]
            results = await asyncio.gather(*tasks)

        db.session.commit()

        flash('Файлы успешно загружены:')

        return render_template('files.html', form=form, results=results)
    return render_template('files.html', form=form)
