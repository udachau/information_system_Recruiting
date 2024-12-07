#Добавить функцию, чтобы если польлзователь уже авотризован его редиректило на главное меню и он не имел доступ к регистрации, если это не сложно
from flask import Blueprint, request, render_template
from dbcm import UseDatabase
import json
from pymysql.err import IntegrityError, OperationalError

reg_blueprint = Blueprint('reg_blueprint', __name__, template_folder='templates')

def check_user_exists(login):
    """Проверяет, существует ли пользователь с указанным логином."""
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        _SQL = """
            SELECT COUNT(*) 
            FROM rec.check_users 
            WHERE user_login = %s
        """
        cursor.execute(_SQL, (login,))
        result = cursor.fetchone()
        return result[0] > 0  # Возвращает True, если пользователь существует

def add_user_to_db(login, password):
    """Добавляет нового пользователя в базу данных."""
    with open('data_files/config.json') as f:
        config = json.load(f)
    with UseDatabase(config) as cursor:
        _SQL = """
            INSERT INTO rec.check_users (user_login, user_pass, group_login, group_pass)
            VALUES (%s, %s, %s, %s)
        """
        print(f"Executing SQL: {_SQL} with params: {login}, {password}, 'guest', '111'")
        cursor.execute(_SQL, (login, password, 'guest', '111'))
        cursor.connection.commit()

@reg_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not all([login, password]):
            return render_template('register.html', error="Все поля обязательны для заполнения.")
        
        try:
            # Проверка, существует ли пользователь
            if check_user_exists(login):
                return render_template('register.html', error="Пользователь с таким логином уже существует.")
            
            # Добавление нового пользователя
            add_user_to_db(login, password)
            return render_template('register_success.html')
        except IntegrityError as e:
            print(f"Ошибка уникальности: {e}")
            return render_template('register.html', error="Логин уже существует.")
        except OperationalError as e:
            print(f"Ошибка подключения: {e}")
            return render_template('error.html', error_msg="Ошибка подключения к базе данных.")
    else:
        return render_template('register.html')
