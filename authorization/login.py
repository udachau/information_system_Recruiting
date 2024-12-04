from flask import Blueprint, session, redirect, request, render_template
from dbcm import UseDatabase
import json
from checker import check_role
from pymysql.err import ProgrammingError, InterfaceError, OperationalError

auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')


def check_user(login, password):
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        _SQL = """
            SELECT `group_login`, `group_pass` 
            FROM rec.check_users 
            WHERE user_login=%s AND user_pass=%s
        """

        cursor.execute(_SQL, (login, password))
        result = cursor.fetchall()

        keys = ['login', 'password']
        result = [dict(zip(keys, user)) for user in result]

    session['db_config'] = config

    return result


@auth_blueprint.route('/auth', methods=['GET', 'POST'])
def auth():
    login = request.form.get('login')
    password = request.form.get('pass')

    if login and password:
        try:
            user = check_user(login, password)
            if user:
                session['db_config']['user'], session['db_config']['password'] = user[0]['login'], user[0]['password']
            else:
                return render_template('loginform.html', wrong=True)

            return redirect('/')

        except OperationalError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось записать протокол!")
    else:
        return render_template('loginform.html')
