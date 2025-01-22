from flask import Blueprint, render_template, session, request, redirect, url_for
from dbcm import UseDatabase
from sql_provider import SQLProvider
from checker import check_role
import json

# Создаём экземпляр SQLProvider
provider = SQLProvider('personal_cabinet/sql')

cabinet_bp = Blueprint('cabinet_bp', __name__, template_folder='templates')

# Получение информации о пользователе
def get_user_info():
    with open('data_files/config.json') as f:
        config = json.load(f)

    query = provider.get('get_user_info.sql')
    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'],))
        result = cursor.fetchone()

    keys = ['name', 'address', 'age', 'sex']
    return dict(zip(keys, result)) if result else {}

# Получение откликов пользователя
def get_user_responses():
    with open('data_files/config.json') as f:
        config = json.load(f)

    query = provider.get('get_user_responses.sql')
    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'],))
        results = cursor.fetchall()

    keys = ['opening_id', 'job_name', 'status']
    return [dict(zip(keys, row)) for row in results]

# Личный кабинет
@cabinet_bp.route('/cabinet', methods=['GET'])
@check_role
def cabinet():
    user_info = get_user_info()
    user_responses = get_user_responses()
    return render_template(
        'cabinet.html',
        user_info=user_info,
        user_login=session['user_info']['user_login'],
        user_responses=user_responses
    )

# Редактирование информации о пользователе
@cabinet_bp.route('/cabinet/edit', methods=['GET', 'POST'])
@check_role
def edit_info():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        age = request.form.get('age')
        sex = request.form.get('sex')

        with open('data_files/config.json') as f:
            config = json.load(f)

        query = provider.get('update_user_info.sql')
        with UseDatabase(config) as cursor:
            cursor.execute(query, (name, address, age, sex, session['user_info']['user_login']))
            cursor.connection.commit()

        return redirect(url_for('cabinet_bp.cabinet'))

    user_info = get_user_info()
    return render_template('edit_info.html', user_info=user_info)

# Отмена отклика
@cabinet_bp.route('/cabinet/cancel_response', methods=['POST'])
@check_role
def cancel_response():
    # Получаем ID вакансии из тела POST-запроса
    opening_id = request.form.get('opening_id')

    if not opening_id:
        return redirect(url_for('cabinet_bp.cabinet'))  # Безопасное поведение при отсутствии ID

    with open('data_files/config.json') as f:
        config = json.load(f)

    # Загружаем SQL-запрос для отмены отклика
    query = provider.get('cancel_response.sql')
    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'], opening_id))
        cursor.connection.commit()

    return redirect(url_for('cabinet_bp.cabinet'))
