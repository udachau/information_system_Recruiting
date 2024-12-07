from flask import Blueprint, render_template, request, redirect, url_for, session
from dbcm import UseDatabase
import json
from checker import check_role

# Создаем Blueprint
vacancy_bp = Blueprint('vacancy_bp', __name__, template_folder='templates')

# Получение данных о вакансиях
def get_open_vacancies():
    with open('data_files/config.json') as f:
        config = json.load(f)

    query = """
        SELECT o.opening_id, p.job_name, o.open_date
        FROM openings o
        JOIN positions p ON o.position_id = p.position_id
        WHERE o.close_date IS NULL
        AND o.opening_id NOT IN (
            SELECT opening_id
            FROM response
            WHERE user_login = %s AND status = 'откликнулся'
        )
        ORDER BY o.open_date DESC
    """

    with UseDatabase(config) as cursor:
        cursor.execute(query, (session['user_info']['user_login'],))
        results = cursor.fetchall()
        print("DEBUG: Vacancies fetched:", results)
    
    keys = ['opening_id', 'job_name', 'open_date']
    print("DEBUG: User login:", session['user_info']['user_login'])
    return [dict(zip(keys, row)) for row in results]

# Маршрут для отображения вакансий
@vacancy_bp.route('/vacancies', methods=['GET'])
@check_role
def vacancies():
    vacancies_list = get_open_vacancies()
    return render_template('vacancies.html', vacancies=vacancies_list)

# Маршрут для отклика на вакансию
@vacancy_bp.route('/vacancies/respond/<int:opening_id>', methods=['POST'])
#@check_role понять почему не работает
def respond_to_vacancy(opening_id):
    with open('data_files/config.json') as f:
        config = json.load(f)

    # Обновление или вставка записи
    query_insert_or_update = """
        INSERT INTO response (user_login, opening_id, status)
        VALUES (%s, %s, 'откликнулся')
        ON DUPLICATE KEY UPDATE status = 'откликнулся'
    """

    with UseDatabase(config) as cursor:
        cursor.execute(query_insert_or_update, (session['user_info']['user_login'], opening_id))
        cursor.connection.commit()

    return redirect(url_for('vacancy_bp.success_page'))

# Маршрут для отображения успешного отклика
@vacancy_bp.route('/vacancies/success', methods=['GET'])
@check_role
def success_page():
    return render_template('response_success.html')