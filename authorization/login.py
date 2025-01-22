from flask import Blueprint, session, redirect, request, render_template
from dbcm import UseDatabase
from sql_provider import SQLProvider
import json
from pymysql.err import OperationalError

auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')
sql_provider = SQLProvider(folder_path='authorization/sql')

def check_user(login, password):
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        query = sql_provider.get('select_user.sql', user_login=login, user_pass=password)
        cursor.execute(query)
        result = cursor.fetchone()
        return result

@auth_blueprint.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('pass')

        if not login or not password:
            return render_template('loginform.html', wrong=True, error_msg="Логин и пароль обязательны для заполнения.")

        try:
            user = check_user(login, password)
            if user:
                # Сохранение информации о пользователе
                session['user_info'] = {'user_login': login}

                # Сохранение конфигурации базы данных
                with open('data_files/config.json') as f:
                    config = json.load(f)
                session['db_config'] = {
                    'host': config['host'],
                    'user': user[0],
                    'password': user[1],
                    'database': config['database']
                }

                # Вывод отладочной информации
                print("DEBUG: session['user_info'] после успешной авторизации:")
                print(session['user_info'])
                print("DEBUG: session['db_config'] после успешной авторизации:")
                print(session['db_config'])

                return redirect('/')
            return render_template('loginform.html', wrong=True, error_msg="Неверный логин или пароль.")
        except OperationalError:
            return render_template('error.html', error_msg="Ошибка подключения к базе данных.")
    return render_template('loginform.html')
