from flask import render_template, redirect, url_for, session, request
from functools import wraps
import json


def check_role(func):
    @wraps(func)                        # позволяет получить атрибуты обернутой функции: func
    def wrapper(*args, **kwargs):
        if 'db_config' not in session:
            return redirect(url_for('auth_blueprint.auth'))

        with open('data_files/roles.json') as f:
            role_mapping = json.load(f)

        for point in role_mapping:
            if point['url'] == request.path and session['db_config']['user'] in point['roles']:
                return func(*args, **kwargs)

        return render_template('user_denied.html', user=session['db_config']['user'])

    return wrapper
