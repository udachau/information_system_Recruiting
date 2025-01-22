from flask import Blueprint, render_template, request, redirect, url_for, session
from dbcm import UseDatabase
from sql_provider import SQLProvider
from checker import check_role
import json
import os

# Создаём экземпляр SQLProvider
provider = SQLProvider('vacancy/sql')

# Создаём Blueprint
vacancy_bp = Blueprint('vacancy_bp', __name__, template_folder='templates')

# Получение данных о вакансиях
def get_open_vacancies():
    with open('data_files/config.json') as f:
        config = json.load(f)

    query = provider.get('get_open_vacancies.sql')
    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'],))
        results = cursor.fetchall()

    keys = ['opening_id', 'job_name', 'open_date']
    return [dict(zip(keys, row)) for row in results]

# Маршрут для отображения вакансий
@vacancy_bp.route('/vacancies', methods=['GET'])
@check_role
def vacancies():
    vacancies_list = get_open_vacancies()
    return render_template('vacancies.html', vacancies=vacancies_list)

# Маршрут для отклика на вакансию (статический endpoint)
@vacancy_bp.route('/vacancies/respond', methods=['POST'])
@check_role
def respond_to_vacancy():
    opening_id = request.form.get('opening_id')  # Получаем ID из тела запроса

    if not opening_id:
        return redirect(url_for('vacancy_bp.vacancies'))  # Безопасное поведение при отсутствии ID

    with open('data_files/config.json') as f:
        config = json.load(f)

    query = provider.get('respond_to_vacancy.sql')
    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'], opening_id))
        cursor.connection.commit()

    return redirect(url_for('vacancy_bp.success_page'))

# Маршрут для отображения успешного отклика
@vacancy_bp.route('/vacancies/success', methods=['GET'])
@check_role
def success_page():
    return render_template('response_success.html')
