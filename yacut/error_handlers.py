from http import HTTPStatus

from flask import jsonify, render_template, request

from . import app, db


class InvalidAPIUsage(Exception):
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)


class MissingBodyError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='Отсутствует тело запроса',
            status_code=HTTPStatus.BAD_REQUEST
        )


class MissingUrlError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='\"url\" является обязательным полем!',
            status_code=HTTPStatus.BAD_REQUEST
        )


class IncorrectUrlError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='Некорректный URL',
            status_code=HTTPStatus.BAD_REQUEST
        )


class BadCustomIdError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='Указано недопустимое имя для короткой ссылки',
            status_code=HTTPStatus.BAD_REQUEST
        )


class CustomIdIsFilesError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='Использование идентификатора files запрещено',
            status_code=HTTPStatus.BAD_REQUEST
        )


class DuplicatedShortIdError(InvalidAPIUsage):
    def __init__(self):
        super().__init__(
            message='Предложенный вариант короткой ссылки уже существует.',
            status_code=HTTPStatus.BAD_REQUEST
        )


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    # Если клиент ожидает JSON (например, Postman или curl с заголовками)
    accept_type = request.accept_mimetypes.best_match(
        ['text/html', 'application/json'])
    if (
        request.path.startswith('/api/')
        or request.is_json
        or accept_type == 'application/json'
    ):
        return jsonify({
            'status': 404,
            'error': 'Not Found',
            'message': 'Запрашиваемый ресурс не найден на сервере.'
        }), HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    accept_type = request.accept_mimetypes.best_match(
            ['text/html', 'application/json'])
    if (
        request.path.startswith('/api/')
        or request.is_json
        or accept_type == 'application/json'
    ):
        return jsonify({
            'status': 500,
            'error': 'Internal Server Error',
            'message': 'Внутренняя ошибка сервера.'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
