from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
from mysql.connector.errors import DatabaseError, InterfaceError, ProgrammingError
from checker import check_role
from sql_provider import SQLProvider
from datetime import date

# Инициализация Blueprint и SQLProvider
interview_bp = Blueprint('interview_bp', __name__, template_folder='templates')
provider = SQLProvider('add_interview/sql')

def get_candidates(cursor):
    query = provider.get('get_candidates.sql')
    cursor.execute(query)
    result = cursor.fetchall()
    keys = ['id', 'name']
    return [dict(zip(keys, line)) for line in result]

def get_openings(cursor, candidate_id):
    query = provider.get('get_openings.sql')
    cursor.execute(query, (candidate_id,))
    result = cursor.fetchall()
    keys = ['id', 'name']
    return [dict(zip(keys, line)) for line in result]

def get_employees(cursor):
    query = provider.get('get_employees.sql')
    cursor.execute(query)
    result = cursor.fetchall()
    keys = ['id', 'name']
    return [dict(zip(keys, line)) for line in result]

def update_response_status(cursor, opening_id, candidate_id, status):
    query = provider.get('update_response_status.sql')
    cursor.execute(query, (status, opening_id, candidate_id))

def get_selected_name(selected_item):
    """Получение имени или названия выбранного элемента."""
    for item in selected_item[0]:  # selected_item[0] — список объектов
        if str(item['id']) == str(selected_item[1]):  # Сравнение ID
            return item['name']
    return "Неизвестно"

@interview_bp.route('/add', methods=['GET', 'POST'])
@check_role
def add_interview():
    today = date.today().isoformat()
    try:
        with UseDatabase(session['db_config']) as cursor:
            candidate = request.form.get('candidate')
            opening = request.form.get('opening')
            employee = request.form.get('employee')
            input_date = request.form.get('date')
            if input_date and input_date < today:
                return render_template('error.html', error_msg="Дата не может быть в прошлом.")
            if candidate:
                session['candidate'] = [get_candidates(cursor), candidate]
                openings_for_candidate = get_openings(cursor, candidate)
                if not openings_for_candidate:
                    return render_template('error.html', error_msg="У выбранного кандидата нет доступных вакансий.")
                return render_template('form_parts.html', part='opening', openings=openings_for_candidate, today=today)
            if opening:
                session['opening'] = [get_openings(cursor, session['candidate'][1]), opening]
                employees = get_employees(cursor)
                return render_template('form_parts.html', part='employee', employees=employees, today=today)
            if employee:
                session['employee'] = [get_employees(cursor), employee]
                return render_template('form_parts.html', part='date', selected=session.get('date'), today=today)
            if input_date:
                session['date'] = input_date
                return render_template('confirm.html',
                                       employee=get_selected_name(session['employee']),
                                       opening=get_selected_name(session['opening']),
                                       candidate=get_selected_name(session['candidate']),
                                       date=input_date)
            candidates_choice = get_candidates(cursor)
            if not candidates_choice:
                return render_template('error.html', error_msg="Нет доступных соискателей с откликами.")
            return render_template('form_parts.html', part='candidate', candidates=candidates_choice, today=today)
    except (ProgrammingError, InterfaceError, DatabaseError) as e:
        return render_template('error.html', error_msg="Произошла ошибка в процессе выполнения!")

@interview_bp.route('/save', methods=['POST'])
@check_role
def save_interview():
    """Сохранение собеседования в базу данных."""
    if not request.form.get('save'):
        return redirect(url_for('interview_bp.add_interview'))
    try:
        with UseDatabase(session['db_config']) as cursor:
            # Получение данных из сессии
            employee_id = session['employee'][1]
            opening_id = session['opening'][1]
            candidate_id = session['candidate'][1]
            date = session['date']

            # Проверка параметров (отладка)
            print(f"DEBUG: date={date}, employee_id={employee_id}, opening_id={opening_id}, candidate_id={candidate_id}")

            # Проверка уникальности
            query_check = provider.get('check_interview.sql')
            cursor.execute(query_check, (date, employee_id, opening_id, candidate_id))
            if cursor.fetchone()[0] > 0:
                return render_template('error.html', error_msg="Собеседование уже существует!")

            # Вставка в interviews
            query_insert_interview = provider.get('insert_interview.sql')
            cursor.execute(query_insert_interview, (date, employee_id, opening_id))
            interview_id = cursor.lastrowid

            # Вставка в interview_details
            query_insert_details = provider.get('insert_interview_details.sql')
            cursor.execute(query_insert_details, (candidate_id, interview_id))

            # Обновление статуса отклика
            update_response_status(cursor, opening_id, candidate_id, 'собеседование назначено')
            cursor.connection.commit()

            return render_template('result.html')

    except Exception as e:
        return render_template('error.html', error_msg=f"Ошибка сохранения: {str(e)}")
    finally:
        # Очистка данных из сессии
        for key in ['employee', 'opening', 'candidate', 'date']:
            session.pop(key, None)
