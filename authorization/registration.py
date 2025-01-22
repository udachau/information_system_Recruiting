from flask import Blueprint, request, render_template, redirect, session
from dbcm import UseDatabase
from sql_provider import SQLProvider
import json
from pymysql.err import IntegrityError, OperationalError

reg_blueprint = Blueprint('reg_blueprint', __name__, template_folder='templates')
sql_provider = SQLProvider(folder_path='authorization/sql')

def check_user_exists(login):
    """Проверяет, существует ли пользователь с указанным логином."""
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        query = sql_provider.get('check_user_exists.sql', user_login=login)
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] > 0  # Возвращает True, если пользователь существует

def add_user_to_db(login, password):
    """Добавляет нового пользователя в базу данных."""
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        query = sql_provider.get('insert_user.sql', user_login=login, user_pass=password)
        cursor.execute(query)
        cursor.connection.commit()

@reg_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not login or not password:
            return render_template('register.html', error="Все поля обязательны для заполнения.")

        try:
            # Проверка, существует ли пользователь
            if check_user_exists(login):
                return render_template('register.html', error="Логин уже занят.")
            
            # Добавление нового пользователя
            add_user_to_db(login, password)
            return render_template('register_success.html')

        except IntegrityError:
            return render_template('register.html', error="Логин уже существует.")
        except OperationalError:
            return render_template('error.html', error_msg="Ошибка подключения к базе данных.")
    return render_template('register.html')
